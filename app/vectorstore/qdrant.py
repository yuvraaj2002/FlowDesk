"""Qdrant client scaffold — connection only, no ingest yet."""

from __future__ import annotations

from typing import Any

from config.qdrant_settings import QdrantSettings
from config.settings import Settings


class QdrantStore:
    """Thin wrapper around local Qdrant. Empty until ingestion lands."""

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
