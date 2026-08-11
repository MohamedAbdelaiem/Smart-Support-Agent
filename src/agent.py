# pyrefly: ignore [missing-import]
from src.tools.refund_check import refund_check, REFUND_CHECK_SCHEMA
# pyrefly: ignore [missing-import]
from src.tools.order_lookup import lookup_order, LOOKUP_ORDER_SCHEMA
# pyrefly: ignore [missing-import]
from src.tools.validation import validate_tool_args
# pyrefly: ignore [missing-import]
from src.client import generate
# pyrefly: ignore [missing-import]
from src.tools.schemas import GROQ_TOOLS
import json


# Registry of available tools and their validation schemas
TOOL_REGISTRY = {
    "lookup_order": lookup_order,
    "refund_check": refund_check,
}

TOOL_SCHEMAS = {
    "lookup_order": LOOKUP_ORDER_SCHEMA,
    "refund_check": REFUND_CHECK_SCHEMA,
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

def run_agent(user_query: str, system_instruction: str, messages: list[dict], max_turns: int = 5) -> dict:
    if not messages:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": user_query})

    for _ in range(max_turns):
        response = generate(system_instruction, messages, tools=GROQ_TOOLS)
        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in assistant_message.tool_calls
                ],
            })
            
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                result = execute_tool(tool_name, tool_args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                })
        else:
            # Model generated final text output
            return {"message": assistant_message.content or ""}

    return {"error": "Exceeded maximum tool execution turns"}
    

    

    