"""Auto-detect the best torch device for local embedding."""

from __future__ import annotations


class DeviceDetector:
    """Pick cuda → mps → cpu unless an explicit device is configured."""

    def resolve(self, configured: str | None = None) -> str:
        if configured and configured.strip() and configured.strip().lower() != "auto":
            return configured.strip().lower()

        try:
            import torch
        except ImportError:
            return "cpu"

        if torch.cuda.is_available():
            return "cuda"
        if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
            return "mps"
        return "cpu"
