# pyrefly: ignore [missing-import]
from src.prompts.prompts import PRODUCT_CATEGORIZATION_SYSTEM
# pyrefly: ignore [missing-import]
from src.tools.schemas import PRODUCT_CATEGORIZATION_OUTPUT_SCHEMA

CLASSIFY_TICKET_TEMPLATE = {
    "id": "classify_ticket",
    "version": "v1",

    "system": PRODUCT_CATEGORIZATION_SYSTEM,

    "user_template": """<ticket>{ticket_text}</ticket>
Classify it.""",

    "output_schema":PRODUCT_CATEGORIZATION_OUTPUT_SCHEMA,
}