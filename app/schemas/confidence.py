"""Answer confidence enum."""

from __future__ import annotations

from enum import StrEnum


class Confidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
