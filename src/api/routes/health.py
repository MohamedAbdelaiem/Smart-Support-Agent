from fastapi import APIRouter
from src.api.schemas import HealthResponse
from src.api.session_manager import session_manager

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint returning service status and active session count."""
    return HealthResponse(
        status="ok",
        service="smart-support-agent",
        sessions_active=session_manager.active_count,
    )
