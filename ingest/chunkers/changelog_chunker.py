"""Chunk changelog entries (one file = one chunk)."""

from __future__ import annotations

from pathlib import Path

from ingest.chunk_id import ChunkIdFactory
from ingest.chunk_record import ChunkRecord
from ingest.frontmatter import FrontmatterParser


class ChangelogChunker:
    """Atomic chunker for `data/changelog/*.md`."""

    def __init__(
        self,
        changelog_dir: Path,
        id_factory: ChunkIdFactory | None = None,
        frontmatter: FrontmatterParser | None = None,
    ) -> None:
        self._changelog_dir = changelog_dir
        self._ids = id_factory or ChunkIdFactory()
        self._frontmatter = frontmatter or FrontmatterParser()

    def chunk_all(self) -> list[ChunkRecord]:
        records: list[ChunkRecord] = []
        for path in sorted(self._changelog_dir.glob("*.md")):
            records.append(self.chunk_file(path))
        return records

    def chunk_file(self, path: Path) -> ChunkRecord:
        raw = path.read_text(encoding="utf-8")
        meta, body = self._frontmatter.parse(raw)
        doc_id = path.stem
        text = body.strip()
        chunk_id = self._ids.build("changelog", doc_id, text)
        affects = meta.get("affects") or []
        if not isinstance(affects, list):
            affects = [affects]

        return ChunkRecord(
            chunk_id=chunk_id,
            text=text,
            payload={
                "chunk_id": chunk_id,
                "doc_id": doc_id,
                "source_type": "changelog",
                "version": None,
                "published_at": str(meta.get("published_at") or ""),
                "is_current": True,
                "superseded_by": None,
                "area": None,
                "trust_level": meta.get("trust_level", "trusted_internal"),
                "heading_path": "",
                "affects": affects,
                "text": text,
                "path": f"data/changelog/{path.name}",
            },
        )
