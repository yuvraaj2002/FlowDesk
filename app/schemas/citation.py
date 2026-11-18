"""Citation pointing at a retrieved source for the UI."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Citation(BaseModel):
    n: int = Field(ge=1)
    doc_id: str | None = None
    source_type: str | None = None
    scope: str | None = None
