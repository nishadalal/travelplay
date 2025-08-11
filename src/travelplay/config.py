import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    model_primary: str
    model_fallbacks: list[str]
    timeout: float
    mock_mode: bool


def get_settings() -> Settings:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    primary = os.getenv("OPENAI_MODEL_PRIMARY")
    fallbacks = [m.strip() for m in os.getenv("OPENAI_MODEL_FALLBACKS").split(",") if m.strip()]
    timeout = float(os.getenv("OPENAI_TIMEOUT", "30"))
    mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"

    return Settings(
        openai_api_key=api_key,
        model_primary=primary,
        model_fallbacks=fallbacks,
        timeout=timeout,
        mock_mode=mock_mode,
    )
