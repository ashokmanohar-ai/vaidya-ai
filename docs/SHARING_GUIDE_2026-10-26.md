# Vaidya AI — Sharing guide (26 October 2026)

**Source:** https://github.com/ashokmanohar-ai/vaidya-ai  
**Intended recipient:** engineer, hiring team, leadership or architecture reviewer.  
**Status:** Synthetic demonstration and an **unapproved clinical-production engineering candidate**. Do not use for actual patient data.

## What's included

| Area | Code | Interpretation |
| --- | --- | --- |
| Local synthetic leadership demo | `app.py`, `scripts/run_demo.py`, `vaidya/` | Flask + LangGraph orchestration, human review, audit and synthetic reports |
| Cloud engineering candidate | `production_app.py`, `production/` | PostgreSQL/checkpoints, worker queue, S3 adapter, access control, Bedrock integration code; not independently validated in a live production environment |
| Tests and release evidence | `tests/`, `production_tests/`, `VALIDATION_REPORT_PRODUCTION.md`, `deployment/PRODUCTION_GATES.md` | Automated/offline checks and explicit pending clinical/security gates |
| Bedrock connectivity diagnostic | `scripts/bedrock_smoke_test.py` | Default invocation makes **no AWS call**; paid synthetic request requires explicit opt-in |

## Review locally (Windows, Python 3.12)

```powershell
git clone https://github.com/ashokmanohar-ai/vaidya-ai.git
cd vaidya-ai
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python scripts\preflight.py
python scripts\validate_complete.py
$env:PORT = "5055"
python scripts\run_demo.py
```

Open `http://127.0.0.1:5055` on **localhost only**. Use fictitious examples exclusively. For the separate candidate's offline tests, install `requirements-production.txt` and run `python -m pytest -q production_tests tests`. A skipped external integration test or green CI must not be called a live-cloud qualification.

## Optional Bedrock validation

```powershell
python scripts\bedrock_smoke_test.py
```

This is the non-billable default. A real Bedrock request requires the owner's prior authorisation, private credentials, `ALLOW_REMOTE_SYNTHETIC_INPUT=true` and `--confirm-cost`. AWS charges may apply. **Never use real patient dictation.**

## Share-safe checklist

- [ ] Check the repository and Git history for leaked keys, .env files, patient identifiers, actual audio or private reports.
- [ ] Link the latest [GitHub Actions run](https://github.com/ashokmanohar-ai/vaidya-ai/actions) and accurately disclose skips and unsupported cloud integration.
- [ ] Explain that human-reviewed synthetic documents are not clinically validated results.
- [ ] Keep demo credentials offline and never host demo login as an internet-facing real application.
- [ ] Do not deploy clinical workloads without security, identity/MFA, privacy, residency, retention, operational recovery and formal clinical/regulatory approvals.

For scope and blockers: [Production overview](../README_PRODUCTION_ENGINEERING.md), [Production gates](../deployment/PRODUCTION_GATES.md), [Security](../SECURITY.md).

**Suggested message when sharing:**

> Vaidya AI demonstrates synthetic-data Flask/LangGraph multi-agent report workflows with doctor approval and an optional Bedrock integration path. The repository also contains a separate cloud engineering candidate for architecture review, not an approved system for real patient data.
