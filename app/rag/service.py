"""Retrieve → prompt → LLM for a grounded chat turn."""

from __future__ import annotations

import asyncio

from app.llm.ollama import OllamaClient
from app.prompts.chat_system import ChatSystemPrompt
from app.rag.context import RagContextBuilder
from app.retrieval.models import RetrievalResult
from app.retrieval.retriever import DenseRetriever
from app.schemas.answer_status import AnswerStatus
from app.schemas.chat_response import ChatResponse
from app.schemas.confidence import Confidence
from config.retrieval_settings import RetrievalSettings
from config.settings import Settings


class RagService:
    """Minimal working RAG: dense retrieve, then answer from evidence only."""

    def __init__(
        self,
        settings: Settings | None = None,
        retriever: DenseRetriever | None = None,
        ollama_client: OllamaClient | None = None,
        system_prompt: ChatSystemPrompt | None = None,
        context_builder: RagContextBuilder | None = None,
    ) -> None:
        self._settings = settings or Settings()
        self._retrieval: RetrievalSettings = self._settings.retrieval
        self._retriever = retriever or DenseRetriever(self._settings)
        self._ollama = ollama_client or OllamaClient(self._settings)
        self._system_prompt = system_prompt or ChatSystemPrompt()
        self._context = context_builder or RagContextBuilder()

    async def answer(
        self,
        *,
        session_id: str,
        message: str,
        account_id: str | None = None,
    ) -> ChatResponse:
        retrieval = await asyncio.to_thread(self._retriever.retrieve, message)
        citations = self._context.build_citations(retrieval.hits)
        status, confidence, flags = self._status_from_retrieval(retrieval)

        if status in {AnswerStatus.REFUSED, AnswerStatus.ESCALATE} and not retrieval.hits:
            return ChatResponse(
                session_id=session_id,
                answer_markdown=(
                    "I don't have enough grounded evidence in the knowledge base "
                    "to answer that. Please escalate to a human agent or rephrase "
                    "with more product context."
                ),
                status=status,
                confidence=confidence,
                guardrail_flags=flags,
                citations=citations,
            )

        evidence = self._context.build_evidence_block(retrieval.hits)
        system_prompt = self._system_prompt.render(
            account_id=account_id,
            evidence=evidence,
        )
        answer = await self._ollama.complete(
            system_prompt=system_prompt,
            user_message=message,
            account_id=account_id,
        )
        return ChatResponse(
            session_id=session_id,
            answer_markdown=answer,
            status=status,
            confidence=confidence,
            guardrail_flags=flags,
            citations=citations,
        )

    def _status_from_retrieval(
        self,
        retrieval: RetrievalResult,
    ) -> tuple[AnswerStatus, Confidence, list[str]]:
        flags = ["rag_dense"]
        if not retrieval.hits:
            flags.append("no_evidence")
            return AnswerStatus.ESCALATE, Confidence.LOW, flags

        top = retrieval.hits[0].score
        threshold = self._retrieval.score_threshold
        if threshold is not None and top < threshold:
            flags.append("below_score_threshold")
            return AnswerStatus.REFUSED, Confidence.LOW, flags

        if top >= 0.75:
            confidence = Confidence.HIGH
        elif top >= 0.55:
            confidence = Confidence.MEDIUM
        else:
            confidence = Confidence.LOW
            flags.append("weak_top_score")

        status = AnswerStatus.ANSWERED if confidence != Confidence.LOW else AnswerStatus.PARTIAL
        return status, confidence, flags
