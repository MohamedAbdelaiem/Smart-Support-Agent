from src.memory.structured_memory import extract_session_facts
from src.tools.refund_check import refund_check
from src.tools.order_lookup import lookup_order
from src.tools.validation import validate_tool_args
from src.client import generate
from src.tools.schemas import GROQ_TOOLS, LOOKUP_ORDER_SCHEMA, REFUND_CHECK_SCHEMA
from src.state import ConversationState
from langsmith import traceable
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

@traceable(name="Execute Tool")
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

@traceable(name="Run Support Agent")
def run_agent(user_query: str, system_instruction: str, state: ConversationState | list[dict], max_turns: int = 5 ,provider ='groq') -> dict:
    # Enforce strict native function calling instructions
    tool_instructions = (
        "\n\nIMPORTANT TOOL INSTRUCTION: When calling tools, generate native tool_calls ONLY. "
        "Do not output function tags or text like <function=...> in your text content."
    )
    full_system_instruction = system_instruction + tool_instructions

    if isinstance(state, ConversationState):
        # Dynamically extract key facts from user input via LLM
        extracted_facts = extract_session_facts(user_query, provider=provider)
        ignored_values = {"not mentioned", "none", "n/a", "unknown", "null", "not specified","unspecified"}
        for key, val in extracted_facts.items():
            if val and str(val).lower() not in ignored_values:
                state.remember(key, str(val))

        state.add_turn("user", user_query)
        messages = state.get_messages(full_system_instruction)
    else:
        messages = state
        if not messages:
            messages.append({"role": "system", "content": full_system_instruction})
        messages.append({"role": "user", "content": user_query})

    executed_tools = []
    for _ in range(max_turns):
        response = generate(system_instruction, messages, tools=GROQ_TOOLS,provider=provider)
        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            assistant_turn = {
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
            }
            messages.append(assistant_turn)
            if isinstance(state, ConversationState):
                state.history.append(assistant_turn)
            
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                
                # Sanitize malformed tool names (e.g., 'refund_check={"order_id": ...}')
                if "=" in tool_name or "{" in tool_name:
                    if "refund_check" in tool_name:
                        tool_name = "refund_check"
                    elif "lookup_order" in tool_name:
                        tool_name = "lookup_order"

                try:
                    tool_args = json.loads(tool_call.function.arguments)
                except Exception:
                    tool_args = {}

                result = execute_tool(tool_name, tool_args)
                executed_tools.append({"name": tool_name, "args": tool_args})

                tool_turn = {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                }
                messages.append(tool_turn)
                if isinstance(state, ConversationState):
                    state.history.append(tool_turn)
        else:
            final_content = assistant_message.content or ""
            if isinstance(state, ConversationState):
                state.add_turn("assistant", final_content)
            return {"message": final_content, "tool_calls": executed_tools}

    return {"error": "Exceeded maximum tool execution turns", "tool_calls": executed_tools}
    

    

    