"""Qdrant connection settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class QdrantSettings(BaseSettings):
    """Local Qdrant endpoint and collection name."""

    model_config = SettingsConfigDict(env_prefix="QDRANT__", extra="ignore")

    url: str = "http://localhost:6333"
    collection: str = "flowdesk_kb"
    prefer_grpc: bool = False
    timeout_seconds: float = 10.0
