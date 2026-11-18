"""Format retrieval hits into prompt evidence + response citations."""

from __future__ import annotations

from app.retrieval.models import RetrievalHit
from app.schemas.citation import Citation


class RagContextBuilder:
    """Turn ranked hits into a numbered evidence block for the LLM."""

    def build_evidence_block(self, hits: list[RetrievalHit]) -> str:
        if not hits:
            return "(no evidence retrieved)"

        parts: list[str] = []
        for index, hit in enumerate(hits, start=1):
            meta = hit.metadata
            source_type = meta.get("source_type") or "unknown"
            doc_id = meta.get("doc_id") or hit.chunk_id
            version = meta.get("version")
            area = meta.get("area")
            heading = meta.get("heading_path") or ""
            header = (
                f"[{index}] source_type={source_type} doc_id={doc_id} "
                f"version={version} area={area} score={hit.score:.4f}"
            )
            if heading:
                header = f"{header} heading={heading}"
            parts.append(f"{header}\n{hit.text.strip()}")
        return "\n\n".join(parts)

    def build_citations(self, hits: list[RetrievalHit]) -> list[Citation]:
        citations: list[Citation] = []
        for index, hit in enumerate(hits, start=1):
            meta = hit.metadata
            version = meta.get("version")
            citations.append(
                Citation(
                    n=index,
                    chunk_id=hit.chunk_id,
                    doc_id=str(meta["doc_id"]) if meta.get("doc_id") is not None else None,
                    version=str(version) if version is not None else None,
                    source_type=(
                        str(meta["source_type"]) if meta.get("source_type") is not None else None
                    ),
                    score=hit.score,
                )
            )
        return citations
