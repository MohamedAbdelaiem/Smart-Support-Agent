import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from src.agent import run_agent
from src.prompts.prompts import PROMPT_V3
from src.api.schemas import ChatRequest, ChatResponse, ResetSessionResponse
from src.api.session_manager import session_manager

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
def chat_sync(request: ChatRequest):
    """
    Synchronous chat endpoint.
    Executes RAG retrieval, runs tools against PostgreSQL, and returns full response.
    """
    state = session_manager.get_or_create(request.session_id)
    if request.customer_name:
        state.remember("customer_name", request.customer_name)
    try:
        result = run_agent(
            user_query=request.user_message,
            system_instruction=PROMPT_V3,
            state=state,
            provider=request.provider,
        )
        return ChatResponse(
            session_id=request.session_id,
            message=result.get("message", ""),
            tool_calls=result.get("tool_calls", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")


@router.post("/stream")
def chat_streaming(request: ChatRequest):
    """
    Server-Sent Events (SSE) streaming endpoint.
    Streams tool events and message text in real time.
    """
    state = session_manager.get_or_create(request.session_id)

    def event_generator():
        try:
            result = run_agent(
                user_query=request.user_message,
                system_instruction=PROMPT_V3,
                state=state,
                provider=request.provider,
            )

            # Yield tool calls event
            tool_calls = result.get("tool_calls", [])
            if tool_calls:
                yield f"data: {json.dumps({'type': 'tool_calls', 'tools': tool_calls})}\n\n"

            # Stream message chunks
            full_message = result.get("message", "")
            words = full_message.split(" ")
            for i, word in enumerate(words):
                chunk = word + (" " if i < len(words) - 1 else "")
                yield f"data: {json.dumps({'type': 'content', 'delta': chunk})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.delete("/{session_id}", response_model=ResetSessionResponse)
def clear_session(session_id: str):
    """Clears conversation history for a given session_id."""
    removed = session_manager.remove(session_id)
    if removed:
        return ResetSessionResponse(
            status="success",
            message=f"Session '{session_id}' has been cleared.",
        )
    return ResetSessionResponse(
        status="not_found",
        message=f"Session '{session_id}' does not exist.",
    )
