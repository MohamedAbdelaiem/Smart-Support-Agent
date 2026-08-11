CLASSIFY_TICKET_TEMPLATE = {
    "id": "classify_ticket",
    "version": "v1",
    "system": """Classify support tickets into: billing, technical, account.
Example: "I was charged twice this month" -> billing
Example: "Can't log in, says my card was declined at signup" -> technical
(the login failure is the real issue, not the card mention -- do not default to billing on money-related keywords alone)""",
    "user_template": """<ticket>{ticket_text}</ticket>\nclassify it.""",
    "output_schema": {
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
    },
}