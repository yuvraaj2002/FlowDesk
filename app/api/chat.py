"""Chat HTTP routes."""

from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter, HTTPException

from app.rag.service import RagService
from app.schemas.chat_request import ChatRequest
from app.schemas.chat_response import ChatResponse

logger = logging.getLogger(__name__)


class ChatRouter:
    """`/chat` backed by dense retrieval + Ollama."""

    def __init__(self, rag_service: RagService | None = None) -> None:
        self._rag = rag_service or RagService()
        self._router = APIRouter(tags=["chat"])
        self._register_routes()

    @property
    def router(self) -> APIRouter:
        return self._router

    def _register_routes(self) -> None:
        self._router.add_api_route(
            "/chat",
            self.chat,
            methods=["POST"],
            response_model=ChatResponse,
        )

    async def chat(self, body: ChatRequest) -> ChatResponse:
        """Retrieve evidence, then answer from it with the local LLM."""
        try:
            return await self._rag.answer(
                session_id=body.session_id,
                message=body.message,
                account_id=body.account_id,
            )
        except httpx.HTTPError as exc:
            logger.exception("Ollama request failed")
            raise HTTPException(
                status_code=502,
                detail=f"Ollama request failed: {exc}",
            ) from exc
        except RuntimeError as exc:
            logger.exception("RAG chat failed")
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
