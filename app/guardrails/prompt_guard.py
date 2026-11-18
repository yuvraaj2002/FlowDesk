"""L1 user-input injection / jailbreak classifier (Prompt Guard family)."""

from __future__ import annotations

from typing import Any

from app.guardrails.models import InjectionScanResult
from config.guard_settings import GuardSettings
from config.settings import Settings
from ingest.device import DeviceDetector


class PromptGuardClassifier:
    """HF sequence classifier for direct jailbreak / injection on user turns."""

    def __init__(
        self,
        settings: Settings | None = None,
        device_detector: DeviceDetector | None = None,
    ) -> None:
        self._settings = settings or Settings()
        self._guard: GuardSettings = self._settings.guard
        self._device = (device_detector or DeviceDetector()).resolve(self._guard.device)
        self._model: Any | None = None
        self._tokenizer: Any | None = None
        self._id2label: dict[int, str] = {}

    @property
    def enabled(self) -> bool:
        return self._guard.enabled

    @property
    def model_name(self) -> str:
        return self._guard.model

    def _ensure_model(self) -> tuple[Any, Any]:
        if self._model is None or self._tokenizer is None:
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            model_id = self._guard.model
            self._tokenizer = AutoTokenizer.from_pretrained(model_id)
            self._model = AutoModelForSequenceClassification.from_pretrained(model_id)
            self._model.to(self._device)
            self._model.eval()
            self._id2label = {
                int(key): str(value) for key, value in self._model.config.id2label.items()
            }
        return self._model, self._tokenizer

    def scan(self, text: str) -> InjectionScanResult:
        cleaned = text.strip()
        if not cleaned:
            return InjectionScanResult(
                flagged=False,
                label="BENIGN",
                score=0.0,
                model=self._guard.model,
            )

        model, tokenizer = self._ensure_model()
        import torch
        from torch.nn.functional import softmax

        inputs = tokenizer(
            cleaned,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        )
        inputs = {key: value.to(self._device) for key, value in inputs.items()}
        with torch.no_grad():
            logits = model(**inputs).logits
            probs = softmax(logits, dim=-1)[0]

        label, score = self._malicious_signal(probs)
        flagged = score >= self._guard.jailbreak_threshold and label != "BENIGN"
        return InjectionScanResult(
            flagged=flagged,
            label=label,
            score=float(score),
            model=self._guard.model,
        )

    def _malicious_signal(self, probs: Any) -> tuple[str, float]:
        """Return the malicious label + score for the loaded model family."""
        labels = {index: name.upper() for index, name in self._id2label.items()}

        # Prompt-Guard-86M: BENIGN / INJECTION / JAILBREAK — user turns use jailbreak.
        jailbreak_idx = next(
            (index for index, name in labels.items() if name == "JAILBREAK"),
            None,
        )
        if jailbreak_idx is not None:
            return "JAILBREAK", float(probs[jailbreak_idx].item())

        # protectai prompt-injection-v2: SAFE / INJECTION
        injection_idx = next(
            (index for index, name in labels.items() if name == "INJECTION"),
            None,
        )
        if injection_idx is not None:
            score = float(probs[injection_idx].item())
            return ("INJECTION" if score >= self._guard.jailbreak_threshold else "SAFE"), score

        top_idx = int(probs.argmax().item())
        return labels.get(top_idx, "UNKNOWN"), float(probs[top_idx].item())
