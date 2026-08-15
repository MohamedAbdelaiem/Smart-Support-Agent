import json
from langsmith import traceable

from src.memory.structured_memory import extract_session_facts
from src.tools.refund_check import refund_check, process_refund
from src.tools.order_lookup import lookup_order
from src.tools.customer_lookup import lookup_customer, list_customers
from src.tools.validation import validate_tool_args
from src.client import generate
from src.tools.schemas import (
    GROQ_TOOLS,
    LOOKUP_ORDER_SCHEMA,
    REFUND_CHECK_SCHEMA,
    PROCESS_REFUND_SCHEMA,
    LOOKUP_CUSTOMER_SCHEMA,
)
from src.state import ConversationState
from src.rag.few_shot_retriever import retrieve_similar_examples, format_few_shot_examples


# Registry of available tools and their validation schemas for LLM execution
TOOL_REGISTRY = {
    "lookup_order": lookup_order,
    "refund_check": refund_check,
    "process_refund": process_refund,
    "lookup_customer": lookup_customer,
}

TOOL_SCHEMAS = {
    "lookup_order": LOOKUP_ORDER_SCHEMA,
    "refund_check": REFUND_CHECK_SCHEMA,
    "process_refund": PROCESS_REFUND_SCHEMA,
    "lookup_customer": LOOKUP_CUSTOMER_SCHEMA,
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
            return {"error": f"Invalid arguments: {err}"}

    # Programmatic Guardrail: Reject placeholder / dummy arguments
    INVALID_PLACEHOLDERS = {
        "your name", "user", "customer", "customer_name", "name",
        "john doe", "jane doe", "unknown", "none", "null", "n/a", "undefined"
    }

    if name == "lookup_customer":
        cust_name = str(raw_input.get("name", "")).strip().lower()
        if not cust_name or cust_name in INVALID_PLACEHOLDERS:
            return {"error": "Invalid argument: Please provide the customer's actual real name."}

    if name in ("lookup_order", "refund_check", "process_refund"):
        order_id = str(raw_input.get("order_id", "")).strip().lower()
        if not order_id or order_id in INVALID_PLACEHOLDERS:
            return {"error": "Invalid argument: Please provide a valid order ID."}

    try:
        return TOOL_REGISTRY[name](**raw_input)
    except Exception as e:
        return {"error": f"Tool execution failed: {e}"}


@traceable(name="Run Support Agent")
def run_agent(
    user_query: str,
    system_instruction: str,
    state: ConversationState | list[dict],
    max_turns: int = 5,
    provider: str = "groq",
) -> dict:
    # Enforce strict native function calling instructions
    tool_instructions = (
        "\n\nIMPORTANT TOOL INSTRUCTION: When calling tools, generate native tool_calls ONLY. "
        "Do not output function tags or text like <function=...> in your text content."
    )

    # RAG context injection
    # 1. Retrieve similar past examples
    similar_examples = retrieve_similar_examples(user_query, top_k=3)
    # 2. Format them into prompt text
    rag_context = format_few_shot_examples(similar_examples)

    # 3. Inject into system instruction
    full_system_instruction = system_instruction + rag_context + tool_instructions

    if isinstance(state, ConversationState):
        # Dynamically extract key facts from user input via LLM
        extracted_facts = extract_session_facts(user_query, provider=provider)
        ignored_values = {"not mentioned", "none", "n/a", "unknown", "null", "not specified", "unspecified"}
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
        response = generate(full_system_instruction, messages, tools=GROQ_TOOLS, provider=provider)
        assistant_message = response.choices[0].message

        # Extract tool calls (either native or parsed from text JSON fallback)
        tool_calls_to_process = []
        if assistant_message.tool_calls:
            for tc in assistant_message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except Exception:
                    args = {}
                tool_calls_to_process.append({"id": tc.id, "name": tc.function.name, "args": args})
        elif assistant_message.content and "function" in assistant_message.content:
            import re
            # Extract individual JSON objects containing "function"
            json_matches = re.findall(r'\{[^{}]*"function"\s*:\s*"[^"]+"[^{}]*\}', assistant_message.content)
            for match in json_matches:
                try:
                    data = json.loads(match)
                    if "function" in data:
                        tool_calls_to_process.append({
                            "id": "call_text_fallback",
                            "name": data["function"],
                            "args": data.get("parameters") or data.get("arguments") or {k: v for k, v in data.items() if k != "function"}
                        })
                except Exception:
                    pass

        if tool_calls_to_process:
            assistant_turn = {
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["args"]),
                        },
                    }
                    for tc in tool_calls_to_process
                ],
            }
            messages.append(assistant_turn)
            if isinstance(state, ConversationState):
                state.history.append(assistant_turn)

            for tc in tool_calls_to_process:
                tool_name = tc["name"]

                # Sanitize malformed tool names
                for valid_name in TOOL_REGISTRY:
                    if valid_name in tool_name:
                        tool_name = valid_name
                        break

                tool_args = tc["args"]
                result = execute_tool(tool_name, tool_args)
                executed_tools.append({"name": tool_name, "args": tool_args})

                tool_turn = {
                    "role": "tool",
                    "tool_call_id": tc["id"],
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