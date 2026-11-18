"""Query-time dense retrieval over the FlowDesk knowledge base."""

from app.retrieval.models import RetrievalHit, RetrievalResult
from app.retrieval.retriever import DenseRetriever

__all__ = ["DenseRetriever", "RetrievalHit", "RetrievalResult"]
