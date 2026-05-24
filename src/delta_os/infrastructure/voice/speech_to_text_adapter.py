"""Speech-to-text adapter interfaces for Phase-1 offline voice scaffolding."""

from __future__ import annotations

from abc import ABC, abstractmethod


class SpeechToTextAdapter(ABC):
    """Interface for speech-to-text adapters."""

    @abstractmethod
    def transcribe(self, audio_bytes: bytes) -> str:
        """Return transcript text for provided audio bytes."""


class NullSpeechToTextAdapter(SpeechToTextAdapter):
    """Deterministic placeholder when no speech backend is configured."""

    def transcribe(self, audio_bytes: bytes) -> str:
        del audio_bytes
        return ""
