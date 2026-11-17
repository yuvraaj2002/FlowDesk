"""Chunk synthetic tickets (subject + resolution indexed)."""

from __future__ import annotations

import json
from pathlib import Path

from ingest.chunk_id import ChunkIdFactory
from ingest.chunk_record import ChunkRecord


class TicketChunker:
    """One chunk per ticket from `data/tickets/tickets.jsonl`."""

    def __init__(
        self,
        tickets_path: Path,
        id_factory: ChunkIdFactory | None = None,
    ) -> None:
        self._tickets_path = tickets_path
        self._ids = id_factory or ChunkIdFactory()

    def chunk_all(self) -> list[ChunkRecord]:
        if not self._tickets_path.is_file():
            return []

        records: list[ChunkRecord] = []
        with self._tickets_path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                ticket = json.loads(line)
                records.append(self.chunk_ticket(ticket))
        return records

    def chunk_ticket(self, ticket: dict) -> ChunkRecord:
        ticket_id = str(ticket["ticket_id"])
        subject = str(ticket.get("subject") or "").strip()
        resolution = str(ticket.get("resolution") or "").strip()
        text = f"{subject}\n\n{resolution}".strip()
        chunk_id = self._ids.build("ticket", ticket_id, text)
        labels = ticket.get("labels") or {}

        return ChunkRecord(
            chunk_id=chunk_id,
            text=text,
            payload={
                "chunk_id": chunk_id,
                "doc_id": ticket_id,
                "source_type": "ticket",
                "version": None,
                "published_at": str(ticket.get("created_at") or "")[:10],
                "is_current": True,
                "superseded_by": None,
                "area": ticket.get("area"),
                "trust_level": "untrusted_customer",
                "heading_path": "",
                "account_id": ticket.get("account_id"),
                "customer_message": ticket.get("customer_message"),
                "subject": subject,
                "resolution": resolution,
                "labels": labels,
                "text": text,
                "path": "data/tickets/tickets.jsonl",
            },
        )
