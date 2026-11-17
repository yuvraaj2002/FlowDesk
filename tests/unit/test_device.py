"""Device auto-detection unit tests."""

from __future__ import annotations

from ingest.device import DeviceDetector


class TestDeviceDetector:
    def test_explicit_device_wins(self) -> None:
        assert DeviceDetector().resolve("cpu") == "cpu"
        assert DeviceDetector().resolve("MPS") == "mps"

    def test_auto_returns_known_backend(self) -> None:
        device = DeviceDetector().resolve("auto")
        assert device in {"cuda", "mps", "cpu"}
