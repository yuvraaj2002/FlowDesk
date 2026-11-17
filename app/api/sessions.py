"""Session HTTP routes."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.session_create_response import SessionCreateResponse
from app.schemas.session_history_response import SessionHistoryResponse
from app.sessions.service import SessionService


class SessionsRouter:
    """Create and inspect chat sessions."""

    def __init__(self, session_service: SessionService | None = None) -> None:
        self._sessions = session_service or SessionService()
        self._router = APIRouter(tags=["sessions"])
        self._register_routes()

    @property
    def router(self) -> APIRouter:
        return self._router

    def _register_routes(self) -> None:
        # Register `/sessions/new` before `/{session_id}` so "new" is not captured.
        self._router.add_api_route(
            "/sessions/new",
            self.create_session,
            methods=["GET"],
            response_model=SessionCreateResponse,
        )
        self._router.add_api_route(
            "/sessions/{session_id}",
            self.get_session,
            methods=["GET"],
            response_model=SessionHistoryResponse,
        )

    async def create_session(self) -> SessionCreateResponse:
        """Return a fresh session id for the UI."""
        return SessionCreateResponse(session_id=self._sessions.create_session_id())

    async def get_session(self, session_id: str) -> SessionHistoryResponse:
        """Conversation history stub — empty until session store exists."""
        return SessionHistoryResponse(session_id=session_id, messages=[])
