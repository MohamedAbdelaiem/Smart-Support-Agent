# pyrefly: ignore [missing-import]
from src.agent import run_agent
# pyrefly: ignore [missing-import]
from src.state import ConversationState

def simulate_long_conversation():
    print("==================================================")
    print("  STAGE 5 DEMO: AUTONOMOUS MEMORY EXTRACTION TEST ")
    print("==================================================\n")

    provider = "openrouter"

    state = ConversationState()
    system_instruction = (
        "You are a helpful customer support agent for Acme Corp. "
        "When checking order details or refund eligibility, ALWAYS execute tool calls using native function calling format. "
        "Do not write function tags like <function=...> in text content."
    )

    # Realistic Customer Turn Sequence
    turns = [
        ("Turn 1", "Hi, my name is Emma Davis and my email is emma.davis@example.com."),
        ("Turn 2", "I am contacting you about my order ORD-1005."),
        ("Turn 3", "I received the package, but the Laptop Stand inside was damaged during transit."),
        ("Turn 4", "Also, please note that I prefer email updates rather than phone calls."),
        ("Turn 5", "What are your standard customer support hours?"),
        ("Turn 6", "Can I request a refund for order ORD-1005 because of the damage?"),
    ]

    for label, user_input in turns:
        print(f"[{label}] User: {user_input}")
        res = run_agent(user_input, system_instruction, state, provider=provider)
        print(f"[{label}] Agent: {res.get('message')}\n")
        print(f"--> Current Remembered Facts: {state.facts}\n")
        print("-" * 50)

    # Final Recall Test: Ask agent to summarize what it knows about the customer
    recall_query = "Can you confirm my name, email, and the order ID we discussed?"
    print(f"\n[Final Recall Test] User: {recall_query}")
    res_final = run_agent(recall_query, system_instruction, state)
    print(f"[Final Recall Test] Agent: {res_final.get('message')}\n")

    print("==================================================")
    print(f"Final Extracted Session Facts: {state.facts}")
    print("==================================================")

if __name__ == "__main__":
    simulate_long_conversation()
