"""Command-line demonstration for the voice module."""

from __future__ import annotations

import argparse
from pathlib import Path

from .base import Transcription
from .service import VoicePipeline
from .speech_to_text import FasterWhisperSTT
from .text_to_speech import Pyttsx3TTS

DISCLAIMER = (
    "I am an automated assistant, not a doctor. I can help collect information "
    "and arrange care. If this may be an emergency, contact local emergency "
    "services now."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Healthcare voice-module demo")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--audio", type=Path, help="Existing audio file to transcribe")
    source.add_argument(
        "--record-seconds",
        type=float,
        help="Record from the default microphone for this duration",
    )
    source.add_argument(
        "--simulate-text",
        help="Skip STT and use text directly for a dependency-light smoke test",
    )
    parser.add_argument("--model", default="small", help="faster-whisper model name")
    parser.add_argument("--language", default=None, help="Optional ISO language code")
    parser.add_argument("--device", default="cpu", choices=("cpu", "cuda"))
    parser.add_argument("--compute-type", default="int8")
    parser.add_argument("--speak", action="store_true", help="Speak the response")
    parser.add_argument("--output-tts", type=Path, help="Save synthesized response")
    parser.add_argument(
        "--recording-path",
        type=Path,
        default=Path("data/runtime/patient_input.wav"),
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    tts = Pyttsx3TTS()

    if args.simulate_text is not None:
        transcription = Transcription(
            text=args.simulate_text,
            language=args.language or "en",
            confidence=1.0,
        )
        pipeline = VoicePipeline(
            stt=FasterWhisperSTT(
                args.model,
                device=args.device,
                compute_type=args.compute_type,
                language=args.language,
            ),
            tts=tts,
        )
    else:
        stt = FasterWhisperSTT(
            args.model,
            device=args.device,
            compute_type=args.compute_type,
            language=args.language,
        )
        pipeline = VoicePipeline(stt=stt, tts=tts)
        if args.audio is not None:
            transcription = pipeline.transcribe_file(args.audio)
        else:
            transcription = pipeline.record_and_transcribe(
                args.record_seconds,
                args.recording_path,
            )

    print(f"Transcript: {transcription.text}")
    print(f"Detected language: {transcription.language or 'unknown'}")
    print(f"Assistant: {DISCLAIMER}")

    pipeline.respond(
        transcription,
        DISCLAIMER,
        speak=args.speak,
        output_audio_path=args.output_tts,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
