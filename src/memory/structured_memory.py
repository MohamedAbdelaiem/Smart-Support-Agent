import json
# pyrefly: ignore [missing-import]
from src.client import generate

MEMORY_EXTRACTION_SYSTEM = """
You are an autonomous memory extraction system for a customer support agent.
Analyze the user's input message and extract key customer/session facts into a clean JSON dictionary.

Target entities to extract if present:
- customer_name: The user's name (e.g., "Alice Smith", "Emma").
- customer_email: Email address mentioned by the user.
- order_id: Any order ID mentioned (e.g., "ORD-1005", "ORD-1001").
- return_reason: Explanation given for wanting a return or refund (e.g., "damaged", "wrong item", "changed mind").
- user_preference: Specific customer requests or preferences (e.g., "prefers email contact", "urgent shipment").

Rules:
- Return ONLY a valid JSON object.
- If an entity is NOT mentioned, do NOT include its key.
- If no entities are found, return `{}`.
"""


def extract_session_facts(user_message: str) -> dict:
    """Uses LLM structured output to extract session facts dynamically from user turns."""
    try:
        response = generate(
            system=MEMORY_EXTRACTION_SYSTEM,
            messages=user_message,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if content:
            return json.loads(content)
    except Exception:
        pass
    return {}
