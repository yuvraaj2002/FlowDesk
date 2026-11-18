"""Unit tests for RAG evidence formatting."""

from __future__ import annotations

from app.rag.context import RagContextBuilder
from app.retrieval.models import RetrievalHit


class TestRagContextBuilder:
    def test_builds_numbered_evidence_and_citations(self) -> None:
        hits = [
            RetrievalHit(
                chunk_id="a",
                score=0.9,
                text="Timeout is 30 seconds.",
                metadata={
                    "doc_id": "workflows/webhook-actions",
                    "source_type": "help_doc",
                    "version": "v3",
                    "area": "workflows",
                    "heading_path": "Timeout",
                },
            )
        ]
        builder = RagContextBuilder()
        block = builder.build_evidence_block(hits)
        citations = builder.build_citations(hits)

        assert "[1] source_type=help_doc" in block
        assert "Timeout is 30 seconds." in block
        assert "heading=Timeout" in block
        assert citations[0].n == 1
        assert citations[0].doc_id == "workflows/webhook-actions"
        assert citations[0].version == "v3"
