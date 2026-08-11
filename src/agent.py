# pyrefly: ignore [missing-import]
from src.tools.order_lookup import lookup_order, LOOKUP_ORDER_SCHEMA
# pyrefly: ignore [missing-import]
from src.tools.validation import validate_tool_args

# Registry of available tools and their validation schemas
TOOL_REGISTRY = {
    "lookup_order": lookup_order,
}

TOOL_SCHEMAS = {
    "lookup_order": LOOKUP_ORDER_SCHEMA,
}


def execute_tool(name: str, raw_input: dict, schema: dict | None = None) -> dict:
    """Executes a tool with argument validation and error handling."""
    if name not in TOOL_REGISTRY:
        return {"error": f"Unknown tool: {name}"}

    tool_schema = schema or TOOL_SCHEMAS.get(name, {})

    if tool_schema:
        valid, err = validate_tool_args(raw_input, tool_schema)
        if not valid:
            return {"error": f"Invalid arguments: {err}"}  # Fed back to model

    try:
        return TOOL_REGISTRY[name](**raw_input)
    except Exception as e:
        return {"error": f"Tool execution failed: {e}"}
