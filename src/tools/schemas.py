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
            "description": "The unique order ID to look up (e.g. ORD-1001 or UUID)",
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
            "description": "The order ID to check refund eligibility for (e.g., 'ORD-1001' or UUID)",
        },
        "reason": {
            "type": "string",
            "description": "Brief explanation for why the refund is being requested",
        },
    },
    "required": ["order_id"],
    "additionalProperties": False,
}

PROCESS_REFUND_SCHEMA = {
    "type": "object",
    "properties": {
        "order_id": {
            "type": "string",
            "description": "The order ID to process and execute a refund for (e.g., 'ORD-1001' or UUID)",
        },
        "customer_id": {
            "type": "string",
            "description": "The customer ID of the order owner to verify authorization",
        },
        "reason": {
            "type": "string",
            "description": "Detailed explanation for processing the refund",
        },
    },
    "required": ["order_id"],
    "additionalProperties": False,
}

LOOKUP_CUSTOMER_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "The full name of the customer to look up (e.g., 'Alice Smith')",
        }
    },
    "required": ["name"],
    "additionalProperties": False,
}

GROQ_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_order",
            "description": "Look up order status, items, delivery date, and total details by order ID",
            "parameters": LOOKUP_ORDER_SCHEMA,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "refund_check",
            "description": "Check if an order is eligible for a refund without executing the refund",
            "parameters": REFUND_CHECK_SCHEMA,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "process_refund",
            "description": "Process and execute an actual refund for an eligible order in the database with customer verification",
            "parameters": PROCESS_REFUND_SCHEMA,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_customer",
            "description": "Look up a customer's ID and account details by their name",
            "parameters": LOOKUP_CUSTOMER_SCHEMA,
        },
    },
]
