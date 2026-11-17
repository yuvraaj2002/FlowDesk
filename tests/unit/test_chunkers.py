"""Unit tests for ingest chunkers (no model download)."""

from __future__ import annotations

from pathlib import Path

from ingest.chunkers.changelog_chunker import ChangelogChunker
from ingest.chunkers.doc_chunker import DocChunker
from ingest.chunkers.ticket_chunker import TicketChunker


class TestChunkers:
    """Chunk shape smoke tests against committed seed data."""

    root = Path(__file__).resolve().parents[2]
    data = root / "data"

    def test_docs_produce_chunks(self) -> None:
        chunks = DocChunker(self.data / "docs").chunk_all()
        assert len(chunks) >= 4
        assert all(chunk.payload["source_type"] == "help_doc" for chunk in chunks)
        assert any("30 seconds" in chunk.text for chunk in chunks)

    def test_changelog_one_file_one_chunk(self) -> None:
        chunks = ChangelogChunker(self.data / "changelog").chunk_all()
        assert len(chunks) == 2
        assert chunks[0].payload["source_type"] == "changelog"

    def test_tickets_index_resolution_not_only_customer_text(self) -> None:
        chunks = TicketChunker(self.data / "tickets" / "tickets.jsonl").chunk_all()
        assert len(chunks) == 4
        sample = next(chunk for chunk in chunks if chunk.payload["doc_id"] == "T-00187")
        assert "Sender ID not registered" in sample.text
        assert "customer_message" in sample.payload
        assert "IGNORE PREVIOUS" not in sample.text or sample.payload["doc_id"] == "T-00301"
