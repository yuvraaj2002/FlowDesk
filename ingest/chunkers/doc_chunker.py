"""Chunk versioned help docs by markdown headings."""

from __future__ import annotations

import re
from pathlib import Path

from ingest.chunk_id import ChunkIdFactory
from ingest.chunk_record import ChunkRecord
from ingest.frontmatter import FrontmatterParser


class DocChunker:
    """Heading-aware chunker for `data/docs/**/*.md` (skips `_manifest`)."""

    _HEADING = re.compile(r"^(#{2,3})\s+(.+)$", re.MULTILINE)

    def __init__(
        self,
        docs_dir: Path,
        id_factory: ChunkIdFactory | None = None,
        frontmatter: FrontmatterParser | None = None,
        max_chars: int = 2400,
    ) -> None:
        self._docs_dir = docs_dir
        self._ids = id_factory or ChunkIdFactory()
        self._frontmatter = frontmatter or FrontmatterParser()
        self._max_chars = max_chars

    def chunk_all(self) -> list[ChunkRecord]:
        records: list[ChunkRecord] = []
        for path in sorted(self._docs_dir.rglob("*.md")):
            if path.name.startswith("_"):
                continue
            records.extend(self.chunk_file(path))
        return records

    def chunk_file(self, path: Path) -> list[ChunkRecord]:
        raw = path.read_text(encoding="utf-8")
        meta, body = self._frontmatter.parse(raw)
        title = self._first_h1(body) or path.stem
        sections = self._split_sections(body)

        doc_id = str(meta.get("doc_id") or path.stem)
        version = meta.get("version")
        records: list[ChunkRecord] = []

        for heading_path, section_text in sections:
            for piece in self._maybe_split(section_text):
                prefix = f"{title}"
                if heading_path:
                    prefix = f"{title} > {heading_path}"
                text = f"{prefix}\n\n{piece}".strip()
                chunk_id = self._ids.build("help_doc", doc_id, str(version), text)
                records.append(
                    ChunkRecord(
                        chunk_id=chunk_id,
                        text=text,
                        payload={
                            "chunk_id": chunk_id,
                            "doc_id": doc_id,
                            "source_type": "help_doc",
                            "version": version,
                            "published_at": str(meta.get("published_at") or ""),
                            "is_current": meta.get("superseded_by") in (None, "null", ""),
                            "superseded_by": meta.get("superseded_by"),
                            "area": meta.get("area"),
                            "trust_level": meta.get("trust_level", "trusted_internal"),
                            "heading_path": heading_path,
                            "text": text,
                            "path": f"data/docs/{path.relative_to(self._docs_dir)}",
                        },
                    )
                )
        return records

    def _first_h1(self, body: str) -> str | None:
        match = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
        return match.group(1).strip() if match else None

    def _split_sections(self, body: str) -> list[tuple[str, str]]:
        matches = list(self._HEADING.finditer(body))
        if not matches:
            cleaned = re.sub(r"^#\s+.+$\n*", "", body, count=1, flags=re.MULTILINE).strip()
            return [("", cleaned)] if cleaned else []

        sections: list[tuple[str, str]] = []
        # Content before first H2/H3 (after H1) is skipped as title-only unless long.
        for index, match in enumerate(matches):
            start = match.end()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
            heading = match.group(2).strip()
            text = body[start:end].strip()
            if text:
                sections.append((heading, text))
        return sections

    def _maybe_split(self, text: str) -> list[str]:
        if len(text) <= self._max_chars:
            return [text]
        chunks: list[str] = []
        paragraphs = text.split("\n\n")
        current = ""
        for para in paragraphs:
            candidate = f"{current}\n\n{para}".strip() if current else para
            if len(candidate) > self._max_chars and current:
                chunks.append(current)
                current = para
            else:
                current = candidate
        if current:
            chunks.append(current)
        return chunks
