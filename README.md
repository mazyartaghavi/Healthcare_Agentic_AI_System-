# Healthcare Agentic AI System with Reinforcement Learning

A complete **synthetic-data research demonstration** combining voice input,
safe conversational orchestration, minimum-necessary mock EHR access, approved
local retrieval-augmented generation, appointment booking, a FastAPI service,
and constrained tabular Q-learning.

> **Safety notice:** This is not a medical device. It does not diagnose,
> prescribe, give dosage advice, or replace emergency services or clinicians.
> Never enter real patient data, credentials, recordings, or API secrets.

## What now works

- local microphone recording, Whisper STT, and offline TTS;
- deterministic emergency escalation outside the LLM/RL policy;
- intent recognition for consultation and appointment workflows;
- synthetic EHR retrieval with consent and field allow-listing;
- approved local knowledge retrieval with source references;
- deterministic safe response composer and optional local Ollama adapter;
- SQLAlchemy/SQLite appointment listing and idempotent confirmed booking;
- append-only hash-chained audit events;
- constrained Q-learning training, evaluation, save, and load;
- FastAPI endpoints, Docker files, and automated tests.

## Install in your existing Anaconda environment

Open Jupyter Notebook in the project folder. In a new cell run:

```python
%pip install -r requirements.txt
%pip install -e .
```

Then use **Kernel → Restart**.

## Run all tests

```python
!python -m pytest -v
```

## End-to-end appointment demonstration in Jupyter

Text workflow:

```python
!python -m healthcare_ai_agent.demo --demo-booking
```

Complete simulated voice-agent pipeline (typed transcript → orchestrator → booking):

```python
!python -m healthcare_ai_agent.voice_agent_demo \
    --simulate-text "I need an appointment" \
    --confirm-first-slot
```

Microphone → Whisper → orchestrator → spoken response:

```python
!python -m healthcare_ai_agent.voice_agent_demo \
    --record-seconds 5 \
    --model tiny \
    --language en \
    --speak
```

The first turn offers available synthetic slots. The second turn simulates an
explicit patient confirmation and creates a synthetic SQLite booking.

## Safe consultation with mock EHR and local RAG

```python
!python -m healthcare_ai_agent.demo     --patient-id SYN-1001     --message "I have a medication question"     --consent
```

## Emergency-gate demonstration

```python
!python -m healthcare_ai_agent.demo     --message "I cannot breathe"
```

The system must escalate immediately and must not retrieve EHR data.

## Train the constrained RL workflow policy

```python
!python -m healthcare_ai_agent.rl.trainer     --episodes 5000     --output runtime/workflow_policy.json
```

The expected evaluation contains `unsafe_actions: 0` and maps `EMERGENCY` to
`ESCALATE_TO_HUMAN`.

## Run the API

In an Anaconda terminal opened in the project folder:

```bash
uvicorn healthcare_ai_agent.api.app:app --reload
```

Open `http://127.0.0.1:8000/docs` in your browser for the interactive API.

Example request body for `POST /consult`:

```json
{
  "patient_id": "SYN-1001",
  "message": "I need an appointment",
  "consent_to_access_ehr": false,
  "preferred_specialty": "general practice",
  "confirm_booking": false
}
```

## Optional Ollama integration

The safe deterministic `TemplateLLM` is the default. To use a locally installed
Ollama server, set:

```text
HEALTHCARE_AGENT_LLM_PROVIDER=ollama
HEALTHCARE_AGENT_OLLAMA_MODEL=gemma3:4b
```

Ollama output remains bounded by the deterministic emergency, access, and action
controls. Do not send real patient information to an unapproved model.

## Docker

```bash
docker compose up --build
```

Docker runs the text/API demonstration. Host microphone and operating-system TTS
are intentionally not configured inside the default container.

## Repository structure

```text
healthcare_ai_agent_starter/
├── config/
├── data/
├── docs/
├── notebooks/
├── src/healthcare_ai_agent/
│   ├── actions/
│   ├── api/
│   ├── conversation/
│   ├── ehr/
│   ├── rag/
│   ├── rl/
│   ├── safety/
│   └── voice/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── main.py
├── pyproject.toml
└── requirements.txt
```

## Production limitations

The repository uses fictional records and local administrative guidance. Real
healthcare deployment requires governed FHIR integration, clinical validation,
identity verification, authorization, encryption and key management, consent
records, secure audit infrastructure, human-oversight procedures, monitoring,
incident response, and jurisdiction-specific legal and regulatory review.
