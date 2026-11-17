"""Hugging Face dense embeddings via sentence-transformers."""

from __future__ import annotations

from config.embed_settings import EmbedSettings
from config.settings import Settings
from ingest.device import DeviceDetector


class HuggingFaceEmbedder:
    """Embed texts with a local HF model (default: BAAI/bge-small-en-v1.5)."""

    def __init__(
        self,
        settings: Settings | None = None,
        device_detector: DeviceDetector | None = None,
    ) -> None:
        self._settings = settings or Settings()
        self._embed: EmbedSettings = self._settings.embed
        self._device_detector = device_detector or DeviceDetector()
        self._device = self._device_detector.resolve(self._embed.device)
        self._model = None

    @property
    def vector_size(self) -> int:
        return self._embed.vector_size

    @property
    def model_name(self) -> str:
        return self._embed.model

    @property
    def device(self) -> str:
        return self._device

    def _ensure_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(
                self._embed.model,
                device=self._device,
            )
        return self._model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        model = self._ensure_model()
        vectors = model.encode(
            texts,
            batch_size=self._embed.batch_size,
            show_progress_bar=len(texts) > 8,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )
        return [vector.tolist() for vector in vectors]
