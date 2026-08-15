from typing import Dict
from src.state import ConversationState


class SessionManager:
    """Thread-safe session state manager mapping session_id to ConversationState."""

    def __init__(self):
        self._sessions: Dict[str, ConversationState] = {}

    def get_or_create(self, session_id: str) -> ConversationState:
        """Retrieves existing ConversationState or creates a new one."""
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationState()
        return self._sessions[session_id]

    def remove(self, session_id: str) -> bool:
        """Deletes session state if it exists."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    @property
    def active_count(self) -> int:
        """Returns the number of active sessions."""
        return len(self._sessions)


# Global singleton instance
session_manager = SessionManager()
