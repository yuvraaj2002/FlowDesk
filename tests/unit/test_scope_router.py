"""Unit tests for the tev1 scope router."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

from app.rag.service import RagService
from app.retrieval.models import RetrievalHit, RetrievalResult
from app.router.models import ScopeDecision, ScopeRouteResult
from app.router.scope import ScopeRouter
from app.schemas.answer_status import AnswerStatus
from config.settings import Settings


class TestScopeRouter:
    def test_maps_systemone_choice(self) -> None:
        client = MagicMock()
        client.decide = AsyncMock(
            return_value={
                "model": "tev1:0.8b",
                "answers": {
                    "scope": {
                        "type": "choice",
                        "choice": "out_of_scope",
                        "probabilities": {
                            "in_scope": 0.04,
                            "out_of_scope": 0.96,
                        },
                        "confidence": 0.76,
                    }
                },
            }
        )
        router = ScopeRouter(settings=Settings(), client=client)
        result = asyncio.run(router.route("Write a poem about cats"))

        assert result.decision == ScopeDecision.OUT_OF_SCOPE
        assert result.confidence == 0.76
        assert result.model == "tev1:0.8b"
        client.decide.assert_awaited_once()


class TestRagServiceRouterGate:
    def test_refuses_out_of_scope_without_retrieval(self) -> None:
        router = MagicMock()
        router.enabled = True
        router.route = AsyncMock(
            return_value=ScopeRouteResult(
                decision=ScopeDecision.OUT_OF_SCOPE,
                confidence=0.9,
                probabilities={"out_of_scope": 0.9, "in_scope": 0.1},
                model="tev1:0.8b",
            )
        )
        retriever = MagicMock()
        ollama = MagicMock()
        ollama.complete = AsyncMock()

        service = RagService(
            settings=Settings(),
            retriever=retriever,
            ollama_client=ollama,
            scope_router=router,
        )
        result = asyncio.run(
            service.answer(
                session_id="sess_1",
                message="Tell me a joke about pirates",
            )
        )

        assert result.status == AnswerStatus.REFUSED
        assert "router_out_of_scope" in result.guardrail_flags
        retriever.retrieve.assert_not_called()
        ollama.complete.assert_not_awaited()

    def test_in_scope_continues_to_rag(self) -> None:
        router = MagicMock()
        router.enabled = True
        router.route = AsyncMock(
            return_value=ScopeRouteResult(
                decision=ScopeDecision.IN_SCOPE,
                confidence=0.8,
                probabilities={"in_scope": 0.9, "out_of_scope": 0.1},
                model="tev1:0.8b",
            )
        )
        retriever = MagicMock()
        retriever.retrieve.return_value = RetrievalResult(
            query="delay",
            top_k=8,
            hits=[
                RetrievalHit(
                    chunk_id="c1",
                    score=0.9,
                    text="Use a Delay step.",
                    metadata={
                        "doc_id": "workflows/delay-steps",
                        "source_type": "help_doc",
                        "version": "v3",
                    },
                )
            ],
        )
        ollama = MagicMock()
        ollama.complete = AsyncMock(return_value="Use a Delay step. [1]")

        service = RagService(
            settings=Settings(),
            retriever=retriever,
            ollama_client=ollama,
            scope_router=router,
        )
        result = asyncio.run(
            service.answer(
                session_id="sess_1",
                message="How do delay steps work?",
            )
        )

        assert result.status == AnswerStatus.ANSWERED
        assert "router_in_scope" in result.guardrail_flags
        assert "rag_dense" in result.guardrail_flags
        retriever.retrieve.assert_called_once()
        ollama.complete.assert_awaited_once()
