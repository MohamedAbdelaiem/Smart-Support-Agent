from typing import List, Dict, Any
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    user_message: str = Field(..., description="The user's support question or message.")
    session_id: str = Field(default="default", description="Unique session identifier for multi-turn history.")
    customer_name: str | None = Field(default=None, description="The selected customer name from UI selector.")
    provider: str = Field(default="openrouter", description="LLM provider: 'openrouter' or 'groq'.")


class ChatResponse(BaseModel):
    session_id: str
    message: str
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    service: str
    sessions_active: int


class ResetSessionResponse(BaseModel):
    status: str
    message: str
