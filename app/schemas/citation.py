"""Citation pointing at a retrieved evidence chunk."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Citation(BaseModel):
    n: int = Field(ge=1)
    chunk_id: str
    doc_id: str | None = None
    version: str | None = None
    source_type: str | None = None
    score: float | None = None
