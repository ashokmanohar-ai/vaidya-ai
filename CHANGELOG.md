# Vaidya AI changelog

Changes below are present in the public repository. This is an engineering history, **not clinical certification**.

## 26 October 2026 — Shareable engineering snapshot

- Hardened the synthetic-only AWS Bedrock smoke-test script: explicit paid-call confirmation, remote input opt-in, model allowlist, safe local diagnostics and suppression of untrusted error messages.
- Fixed production CI setup to install test/demo dependencies when it runs the combined test suite.
- Raised both development and production Pillow dependency ranges to `>=13.0.0,<14` in response to a failing vulnerability audit for Pillow 12.3.0.
- Added regression tests for Bedrock smoke-test cost and opt-in gates and safe errors.
- Added a source-sharing guide and corrected stale README wording about the separate cloud engineering candidate.

**Verification:** Consult [GitHub Actions](https://github.com/ashokmanohar-ai/vaidya-ai/actions) for the latest CI status. Green offline CI does not establish live AWS, Postgres, S3/KMS, clinical correctness, security compliance or suitability for real patients.

## 17 October 2026 — Production engineering foundation

Merged the standalone engineering candidate (Flask API and console, LangGraph Orchestrator, Pathology and Learner graphs, PostgreSQL/checkpoint adapters, queue/worker, private S3, Bedrock provider and governance/approval flow) alongside the retained synthetic local demo. Added tests, developer docs and release gates.

**Never share secrets or identifiable patient data through this repository.**
