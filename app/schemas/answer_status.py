"""Answer status enum."""

from __future__ import annotations

from enum import StrEnum


class AnswerStatus(StrEnum):
    ANSWERED = "answered"
    PARTIAL = "partial"
    REFUSED = "refused"
    ESCALATE = "escalate"
