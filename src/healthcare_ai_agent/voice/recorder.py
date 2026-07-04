"""Microphone capture implemented with sounddevice and soundfile."""

from __future__ import annotations

from pathlib import Path


class MicrophoneRecorder:
    """Record a fixed-duration mono WAV file from the default microphone.

    Imports are intentionally lazy so unit tests and non-audio services can load
    the package on machines without PortAudio devices.
    """

    def __init__(self, sample_rate: int = 16_000, channels: int = 1) -> None:
        if sample_rate < 8_000:
            raise ValueError("sample_rate must be at least 8000 Hz")
        if channels not in (1, 2):
            raise ValueError("channels must be 1 or 2")
        self.sample_rate = sample_rate
        self.channels = channels

    def record(self, duration_seconds: float, output_path: str | Path) -> Path:
        """Capture microphone audio and save a PCM-16 WAV file."""
        if not 0.1 <= duration_seconds <= 300:
            raise ValueError("duration_seconds must be between 0.1 and 300")

        try:
            import sounddevice as sd
            import soundfile as sf
        except ImportError as exc:  # pragma: no cover - environment-specific
            raise RuntimeError(
                "Install sounddevice and soundfile to use microphone capture"
            ) from exc

        destination = Path(output_path).expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        frame_count = int(round(duration_seconds * self.sample_rate))

        try:
            recording = sd.rec(
                frame_count,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="float32",
            )
            sd.wait()
            sf.write(destination, recording, self.sample_rate, subtype="PCM_16")
        except Exception as exc:  # pragma: no cover - hardware-specific
            raise RuntimeError(f"Microphone recording failed: {exc}") from exc

        if not destination.is_file() or destination.stat().st_size == 0:
            raise RuntimeError("Recorder did not create a valid audio file")
        return destination
