"""Interfaces and data models for the voice subsystem."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True, slots=True)
class Transcription:
    """Normalized speech-recognition result."""

    text: str
    language: str | None = None
    confidence: float | None = None
    duration_seconds: float | None = None

    def __post_init__(self) -> None:
        normalized = " ".join(self.text.split())
        object.__setattr__(self, "text", normalized)
        if self.confidence is not None and not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0 and 1")
        if self.duration_seconds is not None and self.duration_seconds < 0:
            raise ValueError("duration_seconds cannot be negative")


class SpeechToText(Protocol):
    """Contract implemented by any speech-to-text backend."""

    def transcribe(self, audio_path: str | Path) -> Transcription:
        """Transcribe an audio file without logging its contents."""


class TextToSpeech(Protocol):
    """Contract implemented by any text-to-speech backend."""

    def speak(self, text: str) -> None:
        """Speak text through the system audio device."""

    def save(self, text: str, output_path: str | Path) -> Path:
        """Synthesize text to an audio file and return its path."""
