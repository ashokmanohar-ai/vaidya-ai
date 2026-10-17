# Vaidya AI delivery architecture

## Deployment stages

**D0 / current:** Flask health + status + synthetic-only public shell. No identity, no clinical data, no background processing.

**D1 / next:** Authenticated doctor/admin development dashboard, persistent PostgreSQL, typed LangGraph graph and durable checkpointing, model-agnostic Bedrock provider adapter. Synthetic fixtures only.

**D2:** Approved audio/image capture and off-request processing. Use private object storage (S3/private Vercel Blob), a durable queue and independent worker for heavy Whisper transcription. Keep clinical source provenance.

**D3:** Doctor-review and sign-off gate; generate only clinician-dictated findings. Correction diff + Learner proposal, admin-controlled skill version activation, rollback and regression evaluation.

## Requirements constraints

From the original PRD: multiple voice notes, freely mixed Tamil/English, separate translation stage, joint content-and-instruction extraction, contextual image placement, branded templates, clinician final version, and 5–10+ report evidence-based learning. No autonomous diagnosis.

## Vercel design constraints

Vercel Functions are stateless. Do not keep authoritative SQLite or reports in the function filesystem. Typical request payload limit is 4.5 MB, so longer audio/images use authenticated direct object-storage uploads. Never start untracked long-running tasks from Flask requests; use a durable queue and appropriately bounded worker. Vercel private previews are not a replacement for application authentication.

## Bedrock design

Provider adapter behind a typed contract. Configure AWS_REGION=ap-south-1, bearer credentials via server-side secrets only, task-specific model IDs via environment. Test account access and data routing for each inference profile; global profiles are not approved for identifiable health data by default.

## Security gates

No real patient inputs before privacy/legal/clinical approval, RBAC, tenant isolation, encrypted storage, audit, backups, data retention, model evaluation and clinician review. Repository should be private.
