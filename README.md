# Vaidya AI — Synthetic-Only Development Foundation

**Status: early infrastructure starter, NOT clinically usable.** No identifiable patient data may be submitted.

Vaidya AI will support clinician-reviewed Histopathology draft generation from Tamil/English voice notes and images, with an administrator-approved correction-learning loop. The initial technology choices are Python/Flask, HTML/Bootstrap, LangGraph, a model-agnostic AWS Bedrock adapter, and PostgreSQL for cloud persistence.

## Local start

Python 3.12 recommended:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:8080. Available routes: `/`, `/health/live`, `/health/ready`, `/api/v1/status`.

## Initial cloud deployment

Connect this repository to a Vercel project. The Flask `app` entrypoint is located in `app.py`. The initial site is a **synthetic-only landing and health-check foundation**, with no medical report intake, real authentication, database access, audio processing, model invocation, or background worker yet.

**Do not put an AWS bearer token, medical records, or private assets in Git.** When implementing Bedrock, use Vercel environment variables and a model-agnostic provider interface. For production report jobs, use a persistent PostgreSQL-backed LangGraph checkpoint store and a durable worker/queue; Vercel Function local filesystem is ephemeral.

## Product safety requirements

- Before any identifiable patient input: private GitHub repository, authenticated app, doctor/hospital access controls, encrypted private storage, approved vendor/region and privacy safeguards.
- Never produce autonomous clinical diagnoses; report only clinician-dictated findings.
- Doctor sign-off before any final report; admin/clinician approval for learned skills.
- Dedicated model evaluation, source grounding, audit logs, failure/retry handling, backup and recovery.

See `docs/ARCHITECTURE.md` for planned rollout.
