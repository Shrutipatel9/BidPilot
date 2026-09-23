# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

BidPilot is a multi-tenant SaaS platform that uses a LangGraph multi-agent workflow to draft answers to RFPs, RFIs, and security/compliance questionnaires (CAIQ, SIG, custom Excel/Word/PDF questionnaires), grounded in a per-organization knowledge base, with human review before export in the original file format.

**Before implementing anything, read `docs/00-INDEX.md`.** It's the map of `docs/` and tells you the minimum set of files to read for the task at hand (which phase file, which section of architecture/ui-ux/testing) instead of loading the full spec every time. `docs/client_requirements.md` is the full source of truth (requirement IDs like `FR-DOC-01` trace back to it) but is large — the index routes you around reading it in full for routine work.

The repo is currently in early scaffold state (Phase 0 of the roadmap): a bare Vite React frontend and a bare FastAPI backend, no database, auth, Docker, or agent pipeline wired up yet.

## Repo layout

- `frontend/` — React (JSX) SPA, built with Vite
- `backend/` — Python FastAPI service, managed with `uv`
- `docs/00-INDEX.md` — **start here**: map of all docs and what to read for each task type
- `docs/client_requirements.md` — full product/requirements spec (source of truth for scope)
- `docs/mvp.md` — **MVP is Phases 0-2**; Phase 3+ is post-MVP, confirm before starting it
- `docs/roadmap.md` + `docs/phases/phase-N-*.md` — phased delivery plan with sub-phases and FR-ID traceability
- `docs/architecture.md` — target system architecture (backend, frontend, data model, agent pipeline, infra)
- `docs/ui-ux.md` — screens, navigation, core user flow, component conventions
- `docs/testing.md` — test strategy per layer, how to run each, AI eval approach

## Commands

### Frontend (`frontend/`)
```
npm run dev       # Vite dev server, http://localhost:5173
npm run build     # production build
npm run preview   # preview the production build
npm run lint      # oxlint
```
No test runner is configured yet.

### Backend (`backend/`)
```
docker compose up -d                       # from repo root: postgres(+pgvector), redis, minio
uv sync                                    # install/sync dependencies into .venv
uv run uvicorn app.main:app --reload       # dev server, http://localhost:8000 (also try `uv run fastapi dev app/main.py`)
uv add <package>                           # add a runtime dependency (updates pyproject.toml + uv.lock)
uv add --dev <package>                     # add a dev-only dependency
uv run pytest                              # run the backend test suite (needs the Compose stack up)
uv run alembic revision --autogenerate -m "..."   # generate a migration from model changes
uv run alembic upgrade head                # apply pending migrations
uv run alembic downgrade -1                # roll back one migration
```
`api`/`web` run natively rather than in Docker Compose — see `docs/architecture.md` §8. No linter/formatter chosen yet for the backend; when adding one, follow `docs/client_requirements.md` §10 rather than picking arbitrarily.

Always run backend Python commands through `uv run ...` (or after `uv sync`, activating `backend/.venv`) rather than a bare system `python`/`pip`, so the right interpreter and locked dependencies are used.

## Architecture (target — see `docs/architecture.md` for full detail)

- **Frontend**: React + Vite talks to the backend over REST and WebSocket/SSE (for streaming agent progress).
- **Backend API** (FastAPI): auth, RBAC, org/project management, knowledge base, billing, exports. Talks to PostgreSQL (+ pgvector for embeddings), Redis (cache/rate-limit/Celery broker), and S3 for file storage.
- **Async work** (Celery workers): document ingestion, drafting runs, exports — not run inline in request handlers.
- **AI orchestration** (LangGraph, invoked from Celery workers): a fixed pipeline of agent nodes — Parser → Classifier → (parallel per-question) Retriever → Drafting → Compliance Checker → Router/Supervisor → either auto-approve, Human Review (LangGraph interrupt/resume), or retry (max 2) → Learning node writes approved answers back into the Answer Library. See §7.2 for the full diagram.
- **AWS AI services**: Bedrock (LLMs + embeddings + Guardrails), Textract (OCR/table extraction), Comprehend (PII detection).

Key invariants to preserve as this gets built out:
- **Tenant isolation is load-bearing**: every DB query and vector search must be filtered by `org_id` (NFR-05); this is meant to be enforced and tested, not assumed.
- **Uploaded document content is data, never instructions** — treat it as untrusted input when it flows into prompts (prompt-injection defense, §7.3).
- **Every factual claim in a drafted answer must cite a retrieved source**; absent a source, the answer must be "Insufficient information" rather than a guess (§7.3, §14).
- Prompts are meant to be versioned/centralized, not inlined ad hoc, per §7.3.

## Working within scope

The project follows a phased roadmap (`docs/roadmap.md`): Phase 0 foundation (current) → Phase 1 basic LLM drafting (no RAG) → Phase 2 RAG → Phase 3 advanced RAG/eval → Phase 4 full LangGraph agent pipeline → Phase 5 AWS AI integration → Phase 6 billing/production hardening → Phase 7 (bonus) Tender Discovery agent, each split into `N.1`/`N.2` sub-phases in `docs/phases/`. When implementing a feature, check which phase/sub-phase it belongs to in `docs/phases/` and avoid pulling in later-phase complexity (e.g. don't wire Celery/LangGraph before Phase 1's basic draft-without-RAG flow exists) unless asked to.

## Development workflow (always follow this loop)

For every sub-phase or feature, in order:

1. **Plan** — read the relevant sub-phase in `docs/phases/phase-N-*.md` (use the `start-phase` skill for this) and work out a concrete implementation plan before writing code.
2. **Ask open questions** — if the sub-phase or the user's request leaves a real ambiguity (a design choice only the user can make, a missing decision the docs don't cover, conflicting requirements), surface it and ask before implementing. Don't silently guess on anything that would be expensive to redo. Don't ask about things the docs already answer, though — check `docs/00-INDEX.md`-routed docs first.
3. **Implement** the plan.
4. **Test properly** before calling it done — per `docs/testing.md` for the layer touched (backend: pytest incl. the mandatory tenant-isolation test for any new tenant-scoped resource; frontend: component tests + a manual run in the dev server; AI-facing changes: check against the grounding/citation rule, not just "it runs"). "It compiles" is not "it's tested."

Don't skip straight to implementation on a multi-step sub-phase without the plan/question pass — that's how scope drifts from what the phase file actually asked for.

## Environment variables, API keys, and credentials

Never invent, silently stub with a fake value, or unilaterally pick a provider/account for anything requiring a secret (AWS keys, Bedrock access, Stripe keys, OpenAI/Anthropic API keys, Google OAuth client ID/secret, database URLs pointing at a real external service, SMTP credentials, etc.).

When implementation needs a new env var or credential:
1. **Stop and ask the user for it** rather than proceeding with a placeholder that would silently no-op or fail later.
2. **Explain concretely how to obtain it** — which console/dashboard, which page, what to click (e.g. "Stripe Dashboard → Developers → API keys, test mode" or "AWS Console → IAM → create a user with `AmazonBedrockFullAccess`, then generate an access key"). Don't just say "get an API key" with no path to it.
3. Add the variable to the relevant `.env.example` with a comment describing what it's for, but never write the real value into a committed file — real values stay in untracked `.env`/`.env.local` files only.
4. If a paid/metered service is involved (Stripe live mode, Bedrock usage, OpenAI usage), say so explicitly so the user isn't surprised by cost.

`backend/.env.example` and `frontend/.env.example` already exist, seeded with Phase 0's known vars — local dev values (DB/Redis/MinIO) are filled in since those aren't external accounts, but external credentials (Google OAuth, email provider) are left blank with a note to ask when that sub-phase actually starts. Extend these files the same way as later phases add vars — don't front-load Phase 5/6 vars (Bedrock, Stripe, ...) before those phases are underway.

## Testing

See `docs/testing.md` for the full strategy (backend pytest, frontend Vitest/RTL, Playwright E2E, AI eval suite) and how to run each. Backend pytest is wired up as of Phase 0.2: async SQLAlchemy against a dedicated `bidpilot_test` database, migrated once per test session and rolled back per-test via a SAVEPOINT (`backend/tests/conftest.py`) — reuse the `db_session`/`client` fixtures rather than inventing a new pattern. Frontend Vitest/RTL and E2E aren't wired up yet; set them up when the phase that needs them starts.

## Project skills and subagents

- **`start-phase` skill** (`.claude/skills/start-phase/`) — invoke (`/start-phase <phase>` or naturally, "start phase 1.2") to begin work on a roadmap phase/sub-phase. It follows `docs/00-INDEX.md`'s reading order automatically instead of loading the whole `docs/` tree. Prefer this over manually re-deriving which docs to read each time.
- **`tenant-isolation-reviewer` subagent** (`.claude/agents/`) — a read-only reviewer for the one invariant that must never regress: every query/route/vector search scoped by `org_id`. Dispatch it after any backend change that adds or touches a database query, an org-scoped API route, or a vector/knowledge-base search — it checks against `docs/architecture.md` §9 and the mandatory isolation-test rule in `docs/testing.md` §2.
