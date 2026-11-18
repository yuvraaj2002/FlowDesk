"""Dense retrieval defaults for query-time search."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class RetrievalSettings(BaseSettings):
    """Top-k and optional score floor for Qdrant dense search."""

    model_config = SettingsConfigDict(env_prefix="RETRIEVAL__", extra="ignore")

    top_k: int = 8
    score_threshold: float | None = None
