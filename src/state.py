class ConversationState:
    def __init__(self):
        self.history: list[dict] = []
        self.facts: dict = {}  

    def add_turn(self, role: str, content):
        """Adds a turn to conversation history."""
        self.history.append({"role": role, "content": content})

    def remember(self, key: str, value: str):
        """Stores a session-scoped fact (e.g. remember('order_id', 'ORD-1001'))."""
        self.facts[key] = value

    def get_messages(self, system_instruction: str) -> list[dict]:
        """Builds formatted messages list for LLM call, appending facts to system prompt."""
        system_content = system_instruction
        if self.facts:
            facts_summary = "\n".join(f"- {k}: {v}" for k, v in self.facts.items())
            system_content += (
                f"\n\n[Internal Customer Context (Do NOT print or echo key=value strings to the customer; speak naturally)]:\n"
                f"{facts_summary}"
            )

        return [{"role": "system", "content": system_content}] + self.history
