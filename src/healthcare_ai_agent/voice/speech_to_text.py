"""Speech-to-text adapters."""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any

from .base import Transcription


class FasterWhisperSTT:
    """Local Whisper transcription through faster-whisper.

    The model is loaded lazily. The first use downloads model weights unless the
    configured model path already exists in the local cache.
    """

    def __init__(
        self,
        model_name: str = "small",
        *,
        device: str = "cpu",
        compute_type: str = "int8",
        language: str | None = None,
    ) -> None:
        if not model_name.strip():
            raise ValueError("model_name cannot be empty")
        self.model_name = model_name
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self._model: Any | None = None

    def _get_model(self) -> Any:
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise RuntimeError(
                    "Install faster-whisper to use FasterWhisperSTT"
                ) from exc
            self._model = WhisperModel(
                self.model_name,
                device=self.device,
                compute_type=self.compute_type,
            )
        return self._model

    def transcribe(self, audio_path: str | Path) -> Transcription:
        source = Path(audio_path).expanduser().resolve()
        if not source.is_file():
            raise FileNotFoundError(f"Audio file not found: {source}")
        if source.stat().st_size == 0:
            raise ValueError("Audio file is empty")

        model = self._get_model()
        try:
            segments, info = model.transcribe(
                str(source),
                language=self.language,
                beam_size=5,
                vad_filter=True,
                condition_on_previous_text=False,
            )
            realized_segments = list(segments)
        except Exception as exc:
            raise RuntimeError(f"Transcription failed: {exc}") from exc

        text = " ".join(segment.text.strip() for segment in realized_segments).strip()
        if not text:
            return Transcription(
                text="",
                language=getattr(info, "language", self.language),
                confidence=0.0,
                duration_seconds=float(getattr(info, "duration", 0.0)),
            )

        log_probs = [
            float(segment.avg_logprob)
            for segment in realized_segments
            if getattr(segment, "avg_logprob", None) is not None
        ]
        confidence = None
        if log_probs:
            confidence = max(0.0, min(1.0, math.exp(sum(log_probs) / len(log_probs))))

        return Transcription(
            text=text,
            language=getattr(info, "language", self.language),
            confidence=confidence,
            duration_seconds=float(getattr(info, "duration", 0.0)),
        )


class MockSTT:
    """Deterministic STT test double; never reads patient audio."""

    def __init__(self, text: str, language: str = "en") -> None:
        self._result = Transcription(text=text, language=language, confidence=1.0)

    def transcribe(self, audio_path: str | Path) -> Transcription:
        _ = audio_path
        return self._result
