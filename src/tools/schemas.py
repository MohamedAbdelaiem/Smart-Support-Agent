PRODUCT_CATEGORIZATION_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "label": {
            "type": "string",
            "enum": ["billing", "technical", "account"],
        },
        "confidence": {
            "type": "string",
            "enum": ["high", "medium", "low"],
        },
    },
    "required": ["label", "confidence"],
    "additionalProperties": False,
}

LOOKUP_ORDER_SCHEMA = {
    "type": "object",
    "properties": {
        "order_id": {
            "type": "string",
            "description": "The unique order ID to look up (e.g. ORD-1001)",
        }
    },
    "required": ["order_id"],
    "additionalProperties": False,
}

REFUND_CHECK_SCHEMA = {
    "type": "object",
    "properties": {
        "order_id": {
            "type": "string",
            "description": "The order ID to check refund eligibility for, e.g., 'ORD-1001'",
        },
        "reason": {
            "type": "string",
            "description": "Brief explanation for why the refund is being requested",
        },
    },
    "required": ["order_id"],
    "additionalProperties": False,
}

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


