from pathlib import Path

import pytest

from healthcare_ai_agent.voice import (
    MicrophoneRecorder,
    MockSTT,
    MockTTS,
    Transcription,
    VoicePipeline,
)


def test_transcription_normalizes_whitespace() -> None:
    result = Transcription(text="  I   need   an appointment.  ", confidence=0.8)
    assert result.text == "I need an appointment."


def test_transcription_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError, match="confidence"):
        Transcription(text="hello", confidence=1.1)


def test_recorder_rejects_unsafe_duration_without_hardware() -> None:
    recorder = MicrophoneRecorder()
    with pytest.raises(ValueError, match="duration_seconds"):
        recorder.record(0.0, "unused.wav")


def test_voice_pipeline_with_test_doubles(tmp_path: Path) -> None:
    stt = MockSTT("I would like to schedule a cardiology appointment.")
    tts = MockTTS()
    pipeline = VoicePipeline(stt=stt, tts=tts)

    transcription = pipeline.transcribe_file(tmp_path / "not-read-by-mock.wav")
    turn = pipeline.respond(
        transcription,
        "A staff-approved response.",
        speak=True,
        output_audio_path=tmp_path / "response.wav",
    )

    assert transcription.confidence == 1.0
    assert turn.response_audio_path is not None
    assert turn.response_audio_path.is_file()
    assert tts.spoken == ["A staff-approved response.", "A staff-approved response."]


def test_pipeline_rejects_empty_response() -> None:
    pipeline = VoicePipeline(MockSTT("hello"), MockTTS())
    with pytest.raises(ValueError, match="response_text"):
        pipeline.respond(Transcription("hello"), "   ")
