# Healthcare Agentic AI System

This package implements the first project increment:

- system architecture and safety boundaries;
- a versioned Python dependency set;
- microphone capture;
- local speech-to-text through `faster-whisper`;
- offline operating-system text-to-speech through `pyttsx3`;
- provider-independent interfaces and unit tests.

It does **not** diagnose, prescribe, or access a real EHR. Use only synthetic
records until clinical, privacy, security, and regulatory reviews are complete.

## Recommended environment

Use CPython 3.11 or 3.12. Python 3.10 is supported by the selected packages, but
3.11 is the reference development target.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# Linux/macOS
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

Linux TTS may also require the system `espeak-ng` package. Microphone recording
requires a working PortAudio input device. The first real STT run downloads the
selected Whisper model.

## Run a dependency-light smoke test

This path skips microphone and STT model loading but exercises the response/TTS
pipeline:

```bash
python -m healthcare_ai_agent.voice.demo \
  --simulate-text "I need to arrange an appointment"
```

Speak the approved disclaimer:

```bash
python -m healthcare_ai_agent.voice.demo \
  --simulate-text "I need to arrange an appointment" \
  --speak
```

## Record and transcribe five seconds

```bash
python -m healthcare_ai_agent.voice.demo \
  --record-seconds 5 \
  --model small \
  --language en
```

## Transcribe an existing file

```bash
python -m healthcare_ai_agent.voice.demo \
  --audio path/to/sample.wav \
  --model small
```

## Run tests

```bash
pytest --cov=healthcare_ai_agent --cov-report=term-missing
```

The tests use deterministic STT/TTS doubles and do not need a microphone, model
download, or cloud API.

## Files

- `docs/ARCHITECTURE.md`: components, trust boundaries, sequence diagram, and RL constraints.
- `requirements.txt`: pinned reference dependencies.
- `src/healthcare_ai_agent/voice/recorder.py`: microphone capture.
- `src/healthcare_ai_agent/voice/speech_to_text.py`: faster-whisper adapter.
- `src/healthcare_ai_agent/voice/text_to_speech.py`: pyttsx3 adapter.
- `src/healthcare_ai_agent/voice/service.py`: composable voice service.
- `tests/test_voice.py`: hardware-independent unit tests.
