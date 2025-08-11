import logging
from typing import Iterable

from langchain.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from openai import (  # error classes for retry classification
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    OpenAIError,
    RateLimitError,
)
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .config import get_settings
from .prompts import SYSTEM_PROMPT, user_prompt
from .schema import Worksheet

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
SETTINGS = get_settings()


def _models_in_order() -> Iterable[str]:
    yield SETTINGS.model_primary
    for m in SETTINGS.model_fallbacks:
        if m != SETTINGS.model_primary:
            yield m


def _make_llm(model_name: str) -> ChatOpenAI:
    return ChatOpenAI(
        model=model_name,
        temperature=0.6,
        timeout=SETTINGS.timeout,
        openai_api_key=SETTINGS.openai_api_key,
        # extra push toward JSON; remove if the model complains
        model_kwargs={"response_format": {"type": "json_object"}},
    )


def _build_chain_for_model(model_name: str) -> Runnable:
    llm = _make_llm(model_name)
    parser = PydanticOutputParser(pydantic_object=Worksheet)
    format_instructions = parser.get_format_instructions()

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT + "\n{format_instructions}"),
            ("user", "{user_input}"),
        ]
    ).partial(format_instructions=format_instructions)

    # prompt -> llm -> parser returns a Worksheet instance
    return prompt | llm | parser


def _build_chain_with_fallbacks() -> Runnable:
    chains = [_build_chain_for_model(m) for m in _models_in_order()]
    if not chains:
        raise RuntimeError("No models configured")
    if len(chains) == 1:
        return chains[0]
    return chains[0].with_fallbacks(chains[1:])


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(
        (RateLimitError, APIConnectionError, APITimeoutError, OpenAIError)
    ),
)
def call_llm_json(age: int, destination: str) -> Worksheet:
    """
    Public entrypoint: build user_input from (age, destination),
    call the chain with fallbacks, and return a validated Worksheet.
    """
    if SETTINGS.mock_mode:
        logging.warning("MOCK_MODE=true → returning canned Worksheet")
        return Worksheet(
            title=f"{destination} Adventure (Age {age})",
            age=age,
            destination=destination,
            fun_facts=[
                f"{destination} has a famous landmark.",
                f"Kids in {destination} love local snacks!",
            ],
            quiz=[
                {"q": "Where are we visiting?", "a": ["Paris", destination, "Rome"], "correct": 1},
                {"q": "How many options per question?", "a": ["2", "3", "5"], "correct": 1},
                {"q": "Should you try local food?", "a": ["No", "Maybe", "Yes"], "correct": 2},
            ],
        )

    chain = _build_chain_with_fallbacks()
    # 🔹 Build the actual user_input string here
    user_input_text = user_prompt(age=age, destination=destination)

    try:
        return chain.invoke({"user_input": user_input_text})
    except AuthenticationError as e:
        logging.error(
            "Auth error: %s\nTips: 1) Use a Project API key with 'model.request' scope. "
            "2) Set OPENAI_ORG_ID/OPENAI_PROJECT if applicable. "
            "3) Verify via curl that the key can list models.",
            e,
        )
        raise
    except BadRequestError as e:
        logging.error("Bad request. Check model name and parameters: %s", e)
        raise
