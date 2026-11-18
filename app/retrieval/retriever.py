"""Embed a text query and retrieve top-k chunks from Qdrant."""

from __future__ import annotations

from typing import Any

from app.retrieval.models import RetrievalHit, RetrievalResult
from app.vectorstore.qdrant import QdrantStore
from config.retrieval_settings import RetrievalSettings
from config.settings import Settings
from ingest.embedder import HuggingFaceEmbedder


class DenseRetriever:
    """Dense cosine retrieval over the FlowDesk knowledge collection."""

    def __init__(
        self,
        settings: Settings | None = None,
        embedder: HuggingFaceEmbedder | None = None,
        store: QdrantStore | None = None,
    ) -> None:
        self._settings = settings or Settings()
        self._retrieval: RetrievalSettings = self._settings.retrieval
        self._embedder = embedder or HuggingFaceEmbedder(self._settings)
        self._store = store or QdrantStore(self._settings)

    def retrieve(self, query: str, *, top_k: int | None = None) -> RetrievalResult:
        cleaned = query.strip()
        if not cleaned:
            raise ValueError("query must be non-empty")

        limit = top_k if top_k is not None else self._retrieval.top_k
        if limit < 1:
            raise ValueError("top_k must be >= 1")

        vector = self._embedder.embed_query(cleaned)
        raw_hits = self._store.search(
            vector,
            limit=limit,
            score_threshold=self._retrieval.score_threshold,
        )
        hits = [self._to_hit(item) for item in raw_hits]
        return RetrievalResult(query=cleaned, top_k=limit, hits=hits)

    def _to_hit(self, item: dict[str, Any]) -> RetrievalHit:
        payload = dict(item.get("payload") or {})
        text = str(payload.pop("text", "") or "")
        chunk_id = str(payload.get("chunk_id") or item.get("id") or "")
        return RetrievalHit(
            chunk_id=chunk_id,
            score=float(item["score"]),
            text=text,
            metadata=payload,
        )
