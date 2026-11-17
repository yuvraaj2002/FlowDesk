"""Qdrant client for FlowDesk knowledge base."""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid5

from config.qdrant_settings import QdrantSettings
from config.settings import Settings

_POINT_NAMESPACE = UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


class QdrantStore:
    """Thin wrapper around local Qdrant for ping / ensure / upsert."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or Settings()
        self._qdrant: QdrantSettings = self._settings.qdrant
        self._client: Any | None = None

    @property
    def client(self) -> Any:
        return self._ensure_client()

    @property
    def collection_name(self) -> str:
        return self._qdrant.collection

    def _ensure_client(self) -> Any:
        if self._client is None:
            from qdrant_client import QdrantClient

            self._client = QdrantClient(
                url=self._qdrant.url,
                prefer_grpc=self._qdrant.prefer_grpc,
                timeout=self._qdrant.timeout_seconds,
            )
        return self._client

    def ping(self) -> bool:
        """Return True if Qdrant responds to a collections list call."""
        self._ensure_client().get_collections()
        return True

    def collection_exists(self) -> bool:
        """Return True if the configured collection is already present."""
        collections = self._ensure_client().get_collections().collections
        return any(item.name == self.collection_name for item in collections)

    def ensure_collection(self, vector_size: int) -> None:
        """Create the KB collection if missing (dense cosine vectors)."""
        from qdrant_client.http import models as qmodels

        if self.collection_exists():
            return

        self._ensure_client().create_collection(
            collection_name=self.collection_name,
            vectors_config=qmodels.VectorParams(
                size=vector_size,
                distance=qmodels.Distance.COSINE,
            ),
        )

    def upsert_embeddings(
        self,
        *,
        chunk_ids: list[str],
        vectors: list[list[float]],
        payloads: list[dict[str, Any]],
    ) -> int:
        """Upsert points keyed by stable chunk_id. Returns point count."""
        from qdrant_client.http import models as qmodels

        if not (len(chunk_ids) == len(vectors) == len(payloads)):
            raise ValueError("chunk_ids, vectors, and payloads must align")

        points = [
            qmodels.PointStruct(
                id=str(uuid5(_POINT_NAMESPACE, chunk_id)),
                vector=vector,
                payload=payload,
            )
            for chunk_id, vector, payload in zip(chunk_ids, vectors, payloads, strict=True)
        ]
        if not points:
            return 0

        self._ensure_client().upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )
        return len(points)

    def count_points(self) -> int:
        if not self.collection_exists():
            return 0
        result = self._ensure_client().count(
            collection_name=self.collection_name,
            exact=True,
        )
        return int(result.count)
