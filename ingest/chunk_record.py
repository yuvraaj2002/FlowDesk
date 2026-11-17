"""One chunk ready for embedding / upsert."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChunkRecord(BaseModel):
    chunk_id: str
    text: str
    payload: dict[str, Any] = Field(default_factory=dict)
