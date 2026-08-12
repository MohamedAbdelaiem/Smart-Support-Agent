import json
# pyrefly: ignore [missing-import]
from src.client import generate
from langsmith import traceable
# pyrefly: ignore [missing-import]
from src.prompts.prompts import MEMORY_EXTRACTION_SYSTEM


@traceable(name="Extract Session Facts")
def extract_session_facts(user_message: str, provider: str = "groq") -> dict:
    """Uses LLM structured output to extract session facts dynamically from user turns."""
    try:
        response = generate(
            system=MEMORY_EXTRACTION_SYSTEM,
            messages=user_message,
            response_format={"type": "json_object"},
            provider=provider,
        )
        content = response.choices[0].message.content
        if content:
            return json.loads(content)
    except Exception:
        pass
    return {}
