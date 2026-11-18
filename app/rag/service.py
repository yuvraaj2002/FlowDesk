"""Retrieve → prompt → LLM for a grounded chat turn."""

from __future__ import annotations

import asyncio

from app.guardrails.prompt_guard import PromptGuardClassifier
from app.llm.ollama import OllamaClient
from app.prompts.chat_system import ChatSystemPrompt
from app.rag.context import RagContextBuilder
from app.retrieval.models import RetrievalResult
from app.retrieval.retriever import DenseRetriever
from app.router.models import ScopeDecision
from app.router.scope import ScopeRouter
from app.schemas.answer_status import AnswerStatus
from app.schemas.block_reason import BlockReason
from app.schemas.chat_response import ChatResponse
from config.retrieval_settings import RetrievalSettings
from config.settings import Settings


class RagService:
    """L1 injection gate → scope gate → dense retrieve → grounded answer."""

    def __init__(
        self,
        settings: Settings | None = None,
        retriever: DenseRetriever | None = None,
        ollama_client: OllamaClient | None = None,
        system_prompt: ChatSystemPrompt | None = None,
        context_builder: RagContextBuilder | None = None,
        scope_router: ScopeRouter | None = None,
        prompt_guard: PromptGuardClassifier | None = None,
    ) -> None:
        self._settings = settings or Settings()
        self._retrieval: RetrievalSettings = self._settings.retrieval
        self._retriever = retriever or DenseRetriever(self._settings)
        self._ollama = ollama_client or OllamaClient(self._settings)
        self._system_prompt = system_prompt or ChatSystemPrompt()
        self._context = context_builder or RagContextBuilder()
        self._scope_router = scope_router or ScopeRouter(self._settings)
        self._prompt_guard = prompt_guard or PromptGuardClassifier(self._settings)

    async def answer(
        self,
        *,
        session_id: str,
        message: str,
        account_id: str | None = None,
    ) -> ChatResponse:
        if self._prompt_guard.enabled:
            scan = await asyncio.to_thread(self._prompt_guard.scan, message)
            if scan.flagged:
                return ChatResponse(
                    session_id=session_id,
                    answer_markdown=(
                        "I can't help with that request. It looks like a prompt "
                        "injection or jailbreak attempt, so I stopped before "
                        "retrieval.\n\n"
                        "Ask a normal FlowDesk support question instead."
                    ),
                    status=AnswerStatus.REFUSED,
                    block_reason=BlockReason.PROMPT_INJECTION,
                    citations=[],
                )

        if self._scope_router.enabled:
            route = await self._scope_router.route(message)
            min_confidence = self._settings.router.min_confidence
            if (
                route.decision == ScopeDecision.OUT_OF_SCOPE
                and route.confidence >= min_confidence
            ):
                return ChatResponse(
                    session_id=session_id,
                    answer_markdown=(
                        "I'm FlowDesk Support Copilot, so I only help with FlowDesk "
                        "product questions — docs, workflows, messaging, billing, "
                        "tickets, and account issues.\n\n"
                        "Rephrase around something in that space, or hand this off "
                        "to a human agent."
                    ),
                    status=AnswerStatus.REFUSED,
                    block_reason=BlockReason.OUT_OF_SCOPE,
                    citations=[],
                )

        retrieval = await asyncio.to_thread(self._retriever.retrieve, message)
        citations = self._context.build_citations(retrieval.hits)
        status = self._status_from_retrieval(retrieval)

        if status in {AnswerStatus.REFUSED, AnswerStatus.ESCALATE} and not retrieval.hits:
            return ChatResponse(
                session_id=session_id,
                answer_markdown=(
                    "I don't have enough grounded evidence in the knowledge base "
                    "to answer that. Please escalate to a human agent or rephrase "
                    "with more product context."
                ),
                status=status,
                block_reason=None,
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
            block_reason=None,
            citations=citations,
        )

    def _status_from_retrieval(self, retrieval: RetrievalResult) -> AnswerStatus:
        if not retrieval.hits:
            return AnswerStatus.ESCALATE

        top = retrieval.hits[0].score
        threshold = self._retrieval.score_threshold
        if threshold is not None and top < threshold:
            return AnswerStatus.REFUSED

        if top < 0.55:
            return AnswerStatus.PARTIAL
        return AnswerStatus.ANSWERED
