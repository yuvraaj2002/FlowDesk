"""Local Hugging Face embedding settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class EmbedSettings(BaseSettings):
    """Dense embedding model used for ingest and query-time retrieval."""

    model_config = SettingsConfigDict(env_prefix="EMBED__", extra="ignore")

    model: str = "BAAI/bge-small-en-v1.5"
    # auto = cuda (NVIDIA) → mps (Apple Silicon) → cpu
    device: str = "auto"
    batch_size: int = 64
    vector_size: int = 384
