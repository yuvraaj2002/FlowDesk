"""Chat HTTP routes."""

from __future__ import annotations

import logging

import httpx
from fastapi import APIRouter, HTTPException

from app.llm.ollama import OllamaClient
from app.prompts.chat_system import ChatSystemPrompt
from app.schemas.answer_status import AnswerStatus
from app.schemas.chat_request import ChatRequest
from app.schemas.chat_response import ChatResponse
from app.schemas.confidence import Confidence

logger = logging.getLogger(__name__)


class ChatRouter:
    """`/chat` backed by Ollama."""

    def __init__(
        self,
        ollama_client: OllamaClient | None = None,
        system_prompt: ChatSystemPrompt | None = None,
    ) -> None:
        self._ollama = ollama_client or OllamaClient()
        self._system_prompt = system_prompt or ChatSystemPrompt()
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
        """Run one turn through the local Ollama model."""
        system_prompt = self._system_prompt.render(account_id=body.account_id)

        try:
            answer = await self._ollama.complete(
                system_prompt=system_prompt,
                user_message=body.message,
                account_id=body.account_id,
            )
        except httpx.HTTPError as exc:
            logger.exception("Ollama request failed")
            raise HTTPException(
                status_code=502,
                detail=f"Ollama request failed: {exc}",
            ) from exc
        except RuntimeError as exc:
            logger.exception("Ollama returned an invalid response")
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        return ChatResponse(
            session_id=body.session_id,
            answer_markdown=answer,
            status=AnswerStatus.ANSWERED,
            confidence=Confidence.MEDIUM,
            guardrail_flags=["ollama_direct"],
        )
