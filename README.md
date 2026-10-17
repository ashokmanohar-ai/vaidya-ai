# VAIDYA AI — Engineering Release Candidate + Synthetic Demo

**Start here:** [`README_PRODUCTION_ENGINEERING.md`](README_PRODUCTION_ENGINEERING.md) · [`VALIDATION_REPORT_PRODUCTION.md`](VALIDATION_REPORT_PRODUCTION.md) · [`deployment/PRODUCTION_GATES.md`](deployment/PRODUCTION_GATES.md)

This repository contains a local synthetic demonstration and a separate security-hardened cloud architecture candidate. **Do not process real patients without validated infrastructure, clinician sign-off, and the legally required privacy/regulatory approvals.**

---

# Vaidya AI — Flask + LangGraph + AWS Bedrock + Multilingual Audio MVP

## Windows startup hotfix — 17 October 2026

This revision fixes an **UnboundLocalError on startup** in `vaidya/multi_agent.py`. The callback functions `await_doctor` and `verify_doctor_approval` are now defined before the Pathology `StateGraph` registers them. No clinical or model behavior was intentionally changed.

If you already installed requirements in your existing `.venv`, simply extract this corrected ZIP to a **fresh folder**, activate the existing or new environment, and run:

```powershell
$env:PORT = '5055'
python scripts\validate_complete.py
python scripts\run_demo.py
```

If starting in a fresh folder without dependencies, first run `python -m pip install -r requirements-dev.txt`.

**Important:** The corrected startup ordering and mocked graph-construction regression test passed in the packaging environment, but native Flask/LangGraph graph execution could not be tested here because those dependencies were unavailable. Run the strict validation script on the Windows laptop before presenting. Do not copy your old `instance/` database into a new demo unless you intentionally wish to preserve previous synthetic state.


**Synthetic-data technical MVP. Not for clinical use.** Updated 17 October 2026.

This source extends the existing Vaidya AI leadership demo. The Flask application includes a deterministic Orchestrator, a Pathology `StateGraph` subgraph, a Learner `StateGraph` subgraph, persistent SQLite LangGraph checkpoints, doctor approval interrupts, and administrator learning approval. The update adds **browser microphone recording and multiple audio uploads, optional faster-whisper CPU ASR, a distinct opt-in Bedrock translation stage, source-vs-extraction warning checks, active approved skill consumption, skill rollback, and audio provenance**.

## Quick-start: offline synthetic leadership demonstration (Windows)

```powershell
cd C:\path\to\vaidya-ai
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python scripts\preflight.py
python scripts\validate_complete.py
$env:PORT='5055'
python scripts\run_demo.py
```

Open `http://127.0.0.1:5055`. If that port is reserved by Windows, set `$env:PORT='8765'` and restart.

Synthetic login credentials (do NOT use on a public deployment):

| Role | Email | Password |
| --- | --- | --- |
| Doctor | `doctor@vaidya.demo` | `DemoDoctor!2026` |
| Administrator | `admin@vaidya.demo` | `DemoAdmin!2026` |

The default settings use `LLM_PROVIDER=demo` and `TRANSLATION_PROVIDER=passthrough`; **no AWS inference occurs**. Click **Load synthetic sample** to test text extraction and report generation. Create a new job to see real LangGraph checkpoint and node traces. Seeded reports are demonstration fixtures, not historical LangGraph executions.

## Enable actual CPU speech-to-text

Install optional audio dependencies:

```powershell
python -m pip install -r requirements-audio.txt
```

Add to `.env`:

```dotenv
ASR_PROVIDER=faster-whisper
WHISPER_MODEL_SIZE=tiny
TRANSLATION_PROVIDER=passthrough
```

The `faster-whisper` model needs an approved initial download (unless `WHISPER_MODEL_PATH` points to an already cached local model). CPU throughput depends on hardware and audio duration. The source handles up to five `WAV/MP3/M4A/WebM/OGG` notes (12 MB per note), preserving their order. A typed transcript can optionally accompany audio. On the **Create Report** page you may record using the browser microphone (localhost permits microphone access) or upload audio files. Audio transcription is real **only if faster-whisper is installed**; missing dependencies cause a clear error, not fake results. No model is downloaded or bundled with this ZIP.

## Enable AWS Bedrock translation AND extraction

```powershell
Copy-Item .env.example .env
notepad .env
```

Configure locally (do not publish credentials):

```dotenv
DEMO_MODE=false
LLM_PROVIDER=bedrock
TRANSLATION_PROVIDER=bedrock
AWS_REGION=ap-south-1
AWS_DEFAULT_REGION=ap-south-1
AWS_BEARER_TOKEN_BEDROCK=<your-own-token-here>
BEDROCK_MODELS=in.openai.gpt-5.6-terra,in.openai.gpt-5.6-luna,global.openai.gpt-5.6-sol,global.anthropic.claude-sonnet-5,global.amazon.nova-2-lite-v1:0,openai.gpt-oss-120b-1:0
LLM_EXTRACTION_MODEL=in.openai.gpt-5.6-terra
LLM_TRANSLATION_MODEL=in.openai.gpt-5.6-luna
ALLOW_REMOTE_SYNTHETIC_INPUT=true
```

**Note:** `DEMO_MODE=false` above is the template default, but `scripts/run_demo.py` sets `DEMO_MODE=true` in-process for the localhost-only demo. Remote Bedrock calls remain disabled unless the separate `ALLOW_REMOTE_SYNTHETIC_INPUT` flag is true. Both translation and extraction may be billed. Model IDs, availability, Converse compatibility, permissions, and region routing have **not** been validated against your AWS account. Global inference profiles may route outside India; never send identifiable patient information to them without approval.

Run the explicit billable smoke test before using Bedrock:

```powershell
python scripts\bedrock_smoke_test.py --confirm-cost
$env:PORT='5055'
python scripts\run_demo.py
```

The Bedrock provider never silently falls back to demo extraction after an AWS error. `LLM_PROVIDER` is model-agnostic at the orchestration layer; the current concrete adapters are Bedrock and deterministic demonstration rules.

## What to demonstrate to leadership

1. Doctor login → Create Report → select a synthetic patient.
2. Use synthetic text or record/upload synthetic dictation (with audio ASR dependency installed).
3. The Orchestrator routes to Pathology `StateGraph`: intake → transcribe → translate → extract → fidelity-check → DOCX renderer → **doctor interrupt**.
4. Inspect original and translated transcripts separately, output, review flags, images, stage trace and checkpoint ID.
5. Edit/approve the synthetic report → checkpoint resumes → Learner analyzes corrections.
6. Admin login → review evidence-backed suggestions, approve/defer/reject via checkpointed interrupt. Approved changes become versioned, and can be rolled back as another immutable version.

## Code layout

| File | Responsibility |
| --- | --- |
| `app.py` | Flask UI, role checks, CSRF, intake and approval routes |
| `vaidya/multi_agent.py` | Parent graph, Pathology/Learner subgraphs, checkpoints/interrupts |
| `vaidya/audio.py` | CPU `faster-whisper` transcription adapter |
| `vaidya/translation.py` | Pass-through or Bedrock translation adapter |
| `vaidya/media.py` | Private, magic-byte checked audio uploads |
| `vaidya/providers.py` | Model-agnostic demo/Bedrock structured extraction |
| `vaidya/fidelity.py` | Conservative numeric/laterality discrepancy warnings |
| `vaidya/database.py` | Local SQLite, auditing, provenance and skill version history |
| `vaidya/reports.py` | Branded DOCX and approved formatting behaviors |
| `tests/` | Domain, mocked-provider, multimedia, LangGraph and Flask tests |
| `scripts/validate_complete.py` | **Strict** Windows testing; fails if Flask/LangGraph integration cannot run |

## Validation and clinical/production boundary

The release report (`VALIDATION_REPORT.md`) separates tests actually run during ZIP creation from tests that require the Windows runtime, live Bedrock, downloaded Whisper weights, and a real clinician. The provided environment did **not** have Flask/LangGraph installed and could not download those dependencies. Domain tests, mocked provider tests, static UI rendering, and ZIP integrity are not a substitute for browser-to-Flask-to-LangGraph real E2E checks.

**Still not production ready:** PostgreSQL checkpoint/database migration, durable cloud job queue, identity lifecycle/MFA and hospital-scale tenant isolation, encrypted private object storage, formal clinical evaluation for Tamil-English, security/regulatory approvals, and verified live AWS performance. This package remains local-only synthetic demo. The included `vercel.json` is not authorization to run the full clinical demo on Vercel Functions.

Never place patient data, bearer tokens, raw transcripts, audio or generated reports in your GitHub repository or a public Vercel deployment.
