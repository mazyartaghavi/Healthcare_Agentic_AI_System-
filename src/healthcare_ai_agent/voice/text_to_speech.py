"""Text-to-speech adapters."""

from __future__ import annotations

import wave
from pathlib import Path
from typing import Any


class Pyttsx3TTS:
    """Offline TTS using the host operating system's speech engine."""

    def __init__(self, *, rate: int = 175, volume: float = 1.0, voice_id: str | None = None) -> None:
        if not 50 <= rate <= 400:
            raise ValueError("rate must be between 50 and 400 words per minute")
        if not 0.0 <= volume <= 1.0:
            raise ValueError("volume must be between 0 and 1")
        self.rate = rate
        self.volume = volume
        self.voice_id = voice_id
        self._engine: Any | None = None

    @staticmethod
    def _validate_text(text: str) -> str:
        normalized = " ".join(text.split())
        if not normalized:
            raise ValueError("text cannot be empty")
        if len(normalized) > 4_000:
            raise ValueError("text is too long for one TTS operation")
        return normalized

    def _get_engine(self) -> Any:
        if self._engine is None:
            try:
                import pyttsx3
            except ImportError as exc:
                raise RuntimeError("Install pyttsx3 to use offline TTS") from exc
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", self.rate)
                engine.setProperty("volume", self.volume)
                if self.voice_id:
                    engine.setProperty("voice", self.voice_id)
            except Exception as exc:  # pragma: no cover - OS-specific
                raise RuntimeError(f"TTS engine initialization failed: {exc}") from exc
            self._engine = engine
        return self._engine

    def speak(self, text: str) -> None:
        normalized = self._validate_text(text)
        engine = self._get_engine()
        try:
            engine.say(normalized)
            engine.runAndWait()
        except Exception as exc:  # pragma: no cover - OS-specific
            raise RuntimeError(f"Speech synthesis failed: {exc}") from exc

    def save(self, text: str, output_path: str | Path) -> Path:
        normalized = self._validate_text(text)
        destination = Path(output_path).expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        engine = self._get_engine()
        try:
            engine.save_to_file(normalized, str(destination))
            engine.runAndWait()
        except Exception as exc:  # pragma: no cover - OS-specific
            raise RuntimeError(f"TTS file synthesis failed: {exc}") from exc
        if not destination.is_file() or destination.stat().st_size == 0:
            raise RuntimeError(
                "The operating-system TTS driver did not create an audio file; "
                "use speak() or configure a supported driver"
            )
        return destination


class MockTTS:
    """Deterministic TTS test double that writes a valid silent WAV file."""

    def __init__(self) -> None:
        self.spoken: list[str] = []

    def speak(self, text: str) -> None:
        normalized = " ".join(text.split())
        if not normalized:
            raise ValueError("text cannot be empty")
        self.spoken.append(normalized)

    def save(self, text: str, output_path: str | Path) -> Path:
        self.speak(text)
        destination = Path(output_path).expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(destination), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16_000)
            wav.writeframes(b"\x00\x00" * 1_600)
        return destination
