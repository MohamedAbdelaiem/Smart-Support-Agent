# pyrefly: ignore [missing-import]
from src.tools.refund_check import REFUND_CHECK_SCHEMA
# pyrefly: ignore [missing-import]
from src.tools.order_lookup import LOOKUP_ORDER_SCHEMA

GROQ_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_order",
            "description": "Look up order status and details by order ID",
            "parameters": LOOKUP_ORDER_SCHEMA,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "refund_check",
            "description": "Check if an order is eligible for a refund",
            "parameters": REFUND_CHECK_SCHEMA,
        },
    },
]

