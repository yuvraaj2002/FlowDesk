"""Dense retriever unit tests (mocked embedder + store)."""

from __future__ import annotations

import pytest

from app.retrieval.retriever import DenseRetriever
from config.settings import Settings


class _FakeEmbedder:
    model_name = "fake"
    device = "cpu"
    vector_size = 3

    def embed_query(self, text: str) -> list[float]:
        assert text
        return [0.1, 0.2, 0.3]


class _FakeStore:
    def __init__(self, hits: list[dict] | None = None) -> None:
        self._hits = hits or []
        self.last_search: dict | None = None

    def search(
        self,
        vector: list[float],
        *,
        limit: int = 8,
        score_threshold: float | None = None,
    ) -> list[dict]:
        self.last_search = {
            "vector": vector,
            "limit": limit,
            "score_threshold": score_threshold,
        }
        return self._hits[:limit]


class TestDenseRetriever:
    def test_retrieve_maps_payload_to_hit(self) -> None:
        store = _FakeStore(
            hits=[
                {
                    "id": "point-1",
                    "score": 0.91,
                    "payload": {
                        "chunk_id": "chk_delay",
                        "source_type": "help_doc",
                        "area": "workflows",
                        "text": "Delay steps wait between actions.",
                    },
                }
            ]
        )
        retriever = DenseRetriever(
            settings=Settings(),
            embedder=_FakeEmbedder(),  # type: ignore[arg-type]
            store=store,  # type: ignore[arg-type]
        )

        result = retriever.retrieve("How do delay steps work?", top_k=3)

        assert result.query == "How do delay steps work?"
        assert result.top_k == 3
        assert len(result.hits) == 1
        hit = result.hits[0]
        assert hit.chunk_id == "chk_delay"
        assert hit.score == pytest.approx(0.91)
        assert hit.text == "Delay steps wait between actions."
        assert hit.metadata["source_type"] == "help_doc"
        assert hit.metadata["area"] == "workflows"
        assert "text" not in hit.metadata
        assert store.last_search is not None
        assert store.last_search["limit"] == 3
        assert store.last_search["vector"] == [0.1, 0.2, 0.3]

    def test_empty_query_raises(self) -> None:
        retriever = DenseRetriever(
            settings=Settings(),
            embedder=_FakeEmbedder(),  # type: ignore[arg-type]
            store=_FakeStore(),  # type: ignore[arg-type]
        )
        with pytest.raises(ValueError, match="non-empty"):
            retriever.retrieve("   ")
