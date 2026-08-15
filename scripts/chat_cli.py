from src.agent import run_agent
from src.prompts.prompts import PROMPT_V3
from src.state import ConversationState
from src.rag.few_shot_retriever import retrieve_similar_examples


def main():
    print("=" * 60)
    print("🤖 Smart Support Agent (RAG-Enabled Interactive CLI)")
    print("Type your message and press Enter. (Type 'exit' or 'q' to quit)")
    print("=" * 60 + "\n")

    state = ConversationState()

    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit", "q"):
                print("Goodbye!")
                break

            # 1. Preview RAG retrieval
            similar_examples = retrieve_similar_examples(user_input, top_k=2)
            print(f"\n🔍 [RAG Retrieved {len(similar_examples)} Golden Examples]:")
            for i, ex in enumerate(similar_examples, 1):
                print(f"   {i}. ({ex['category']}) \"{ex['user_query'][:60]}...\"")

            # 2. Run agent with Few-Shot RAG
            result = run_agent(
                user_query=user_input,
                system_instruction=PROMPT_V3,
                state=state,
                provider="openrouter",
            )

            # 3. Print executed tools & agent response
            tools_used = [t["name"] for t in result.get("tool_calls", [])]
            if tools_used:
                print(f"⚙️  [Tools Executed]: {', '.join(tools_used)}")

            print(f"\n🤖 Agent:\n{result.get('message')}\n")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
