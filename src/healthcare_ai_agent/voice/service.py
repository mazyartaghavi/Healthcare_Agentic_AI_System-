"""Application service that composes recording, STT, and TTS."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .base import SpeechToText, TextToSpeech, Transcription
from .recorder import MicrophoneRecorder


@dataclass(frozen=True, slots=True)
class VoiceTurn:
    """One voice interaction result without raw audio or PHI logging."""

    transcription: Transcription
    response_text: str
    response_audio_path: Path | None = None


class VoicePipeline:
    """Provider-independent voice pipeline.

    This layer performs no diagnosis and makes no appointment decision. It only
    converts audio to text and approved response text back to speech.
    """

    def __init__(
        self,
        stt: SpeechToText,
        tts: TextToSpeech,
        recorder: MicrophoneRecorder | None = None,
    ) -> None:
        self.stt = stt
        self.tts = tts
        self.recorder = recorder or MicrophoneRecorder()

    def transcribe_file(self, audio_path: str | Path) -> Transcription:
        return self.stt.transcribe(audio_path)

    def record_and_transcribe(
        self,
        duration_seconds: float,
        temporary_audio_path: str | Path,
    ) -> Transcription:
        audio_path = self.recorder.record(duration_seconds, temporary_audio_path)
        return self.stt.transcribe(audio_path)

    def respond(
        self,
        transcription: Transcription,
        response_text: str,
        *,
        speak: bool = False,
        output_audio_path: str | Path | None = None,
    ) -> VoiceTurn:
        normalized_response = " ".join(response_text.split())
        if not normalized_response:
            raise ValueError("response_text cannot be empty")

        audio_path: Path | None = None
        if output_audio_path is not None:
            audio_path = self.tts.save(normalized_response, output_audio_path)
        if speak:
            self.tts.speak(normalized_response)

        return VoiceTurn(
            transcription=transcription,
            response_text=normalized_response,
            response_audio_path=audio_path,
        )
