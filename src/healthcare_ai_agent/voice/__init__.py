"""Voice capture, transcription, and speech synthesis adapters."""

from .base import SpeechToText, TextToSpeech, Transcription
from .recorder import MicrophoneRecorder
from .speech_to_text import FasterWhisperSTT, MockSTT
from .text_to_speech import MockTTS, Pyttsx3TTS
from .service import VoicePipeline, VoiceTurn

__all__ = [
    "FasterWhisperSTT",
    "MicrophoneRecorder",
    "MockSTT",
    "MockTTS",
    "Pyttsx3TTS",
    "SpeechToText",
    "TextToSpeech",
    "Transcription",
    "VoicePipeline",
    "VoiceTurn",
]
