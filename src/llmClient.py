
# pyrefly: ignore [missing-import]
from src.client import generate

class LLMClient:
    def __init__(self, provider: str = "groq"):
        self.provider = provider.lower()
    
    def chat(self, system: str, messages: list, tools: list | None = None):
        return generate(
            system=system,
            messages=messages,
            provider=self.provider,
            model=self.model,
            tools=tools
        )