SYSTEM_PROMPT = """You are an educational content generator for children.
Return STRICT JSON only (no code fences, no prose).
The JSON must match the provided schema keys and types exactly.
Keep vocabulary age-appropriate and culturally respectful.
"""


def user_prompt(age: int, destination: str) -> str:
    return f"""Create a small worksheet for a child.

Requirements:
- age: {age}
- destination: {destination}
- 2-3 fun facts (short, engaging)
- 3 quiz questions, each with 3 options and correct index

Output JSON keys:
- title (string)
- age (int)
- destination (string)
- fun_facts (list of strings)
- quiz (list of items: {{q, a, correct}})

Return ONLY valid JSON."""
