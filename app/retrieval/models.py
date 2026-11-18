"""Typed results for dense KB retrieval."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RetrievalHit(BaseModel):
    """One ranked chunk from the vector store."""

    chunk_id: str
    score: float
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalResult(BaseModel):
    """Query plus the top-k hits returned for it."""

    query: str
    top_k: int
    hits: list[RetrievalHit] = Field(default_factory=list)
