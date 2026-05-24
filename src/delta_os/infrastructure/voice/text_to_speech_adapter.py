"""Text-to-speech adapter interfaces for Phase-1 offline voice scaffolding."""

from __future__ import annotations

from abc import ABC, abstractmethod


class TextToSpeechAdapter(ABC):
    """Interface for text-to-speech adapters."""

    @abstractmethod
    def speak(self, text: str) -> str:
        """Emit speech for text and return a deterministic status token."""


class LocalTextToSpeechStub(TextToSpeechAdapter):
    """Deterministic local TTS stub with optional mute behavior."""

    def __init__(self, *, muted: bool = False) -> None:
        self._muted = muted
        self._last_text = ""

    @property
    def muted(self) -> bool:
        return self._muted

    @property
    def last_text(self) -> str:
        return self._last_text

    def set_muted(self, value: bool) -> None:
        self._muted = value

    def speak(self, text: str) -> str:
        self._last_text = text
        if self._muted:
            return "muted"
        return "spoken"
