"""
MCP Context Management.
"""

import uuid
from typing import Any


class ContextManager:
    """
    Manages conversation context and session state for MCP.
    """

    def __init__(self):
        self._sessions: dict[str, dict[str, Any]] = {}

    def create_session(self) -> str:
        """Create a new session and return its ID."""
        session_id = str(uuid.uuid4())
        self._sessions[session_id] = {"history": [], "variables": {}}
        return session_id

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """Retrieve session data."""
        return self._sessions.get(session_id)

    def add_message(self, session_id: str, role: str, content: str):
        """Add a message to the session history."""
        if session := self.get_session(session_id):
            session["history"].append({"role": role, "content": content})

    def clear_session(self, session_id: str):
        """Clear session history."""
        if session_id in self._sessions:
            self._sessions[session_id]["history"] = []


# Global instance
context_manager = ContextManager()
