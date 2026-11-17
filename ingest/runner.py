"""Orchestrate chunk → embed → Qdrant upsert."""

from __future__ import annotations

from pathlib import Path

from app.vectorstore.qdrant import QdrantStore
from config.settings import Settings
from ingest.chunk_record import ChunkRecord
from ingest.chunkers.changelog_chunker import ChangelogChunker
from ingest.chunkers.doc_chunker import DocChunker
from ingest.chunkers.ticket_chunker import TicketChunker
from ingest.embedder import HuggingFaceEmbedder


class IngestRunner:
    """Standalone knowledge-base ingest for docs, changelogs, and tickets."""

    def __init__(
        self,
        data_dir: Path | None = None,
        settings: Settings | None = None,
        embedder: HuggingFaceEmbedder | None = None,
        store: QdrantStore | None = None,
    ) -> None:
        root = Path(__file__).resolve().parents[1]
        self._data_dir = data_dir or (root / "data")
        self._settings = settings or Settings()
        self._embedder = embedder or HuggingFaceEmbedder(self._settings)
        self._store = store or QdrantStore(self._settings)

    def run(self, sources: list[str] | None = None) -> dict[str, object]:
        selected = set(sources or ["docs", "changelog", "tickets"])
        chunks: list[ChunkRecord] = []

        if "docs" in selected:
            chunks.extend(DocChunker(self._data_dir / "docs").chunk_all())
        if "changelog" in selected:
            chunks.extend(ChangelogChunker(self._data_dir / "changelog").chunk_all())
        if "tickets" in selected:
            chunks.extend(
                TicketChunker(self._data_dir / "tickets" / "tickets.jsonl").chunk_all()
            )

        self._store.ensure_collection(self._embedder.vector_size)
        if not chunks:
            return {
                "chunks": 0,
                "upserted": 0,
                "collection_points": self._store.count_points(),
                "embed_model": self._embedder.model_name,
                "device": self._embedder.device,
            }

        texts = [chunk.text for chunk in chunks]
        vectors = self._embedder.embed_documents(texts)
        upserted = self._store.upsert_embeddings(
            chunk_ids=[chunk.chunk_id for chunk in chunks],
            vectors=vectors,
            payloads=[chunk.payload for chunk in chunks],
        )
        return {
            "chunks": len(chunks),
            "upserted": upserted,
            "collection_points": self._store.count_points(),
            "embed_model": self._embedder.model_name,
            "device": self._embedder.device,
        }
