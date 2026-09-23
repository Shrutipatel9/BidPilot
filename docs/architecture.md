# BidPilot Architecture

Target architecture for the system. Sections are written to be read independently — jump to the one relevant to your current phase/sub-phase rather than reading top to bottom (see `docs/00-INDEX.md`). This describes the target state from `docs/client_requirements.md` §7/§10/§11; what's actually implemented so far is tracked by which phase/sub-phase is checked off in `docs/roadmap.md`.

## 1. System overview

```
            ┌────────────────────────────┐
            │     React Web App (SPA)    │
            └─────────────┬──────────────┘
                          │ REST + WebSocket/SSE
            ┌─────────────▼──────────────┐
            │      FastAPI Backend       │── Stripe (Checkout, Webhooks)
            │ Auth · RBAC · Projects ·   │
            │ KB · Billing · Exports     │
            └──┬──────────┬──────────┬───┘
               │          │          │
        ┌──────▼───┐ ┌────▼────┐ ┌───▼─────────────┐
        │PostgreSQL│ │  Redis  │ │ S3 (files)      │
        │+ pgvector│ │cache/q  │ └─────────────────┘
        └──────▲───┘ └────┬────┘
               │          │ tasks
        ┌──────┴──────────▼────────────────────────┐
        │   Celery Workers + LangGraph Agents       │
        │ Parser · Classifier · Retriever · Drafter │
        │ Compliance · Router · Learning · Scout    │
        └──────┬───────────────────────────────────┘
               │
   ┌───────────▼──────────────────────────────────────┐
   │ AWS AI: Bedrock (LLM/Embeddings/Guardrails/KB),  │
   │ Textract, Comprehend  ·  Langfuse/LangSmith      │
   └──────────────────────────────────────────────────┘
```

The frontend never talks to Postgres/Redis/S3/AWS AI directly — everything goes through the FastAPI backend. Long-running work (ingestion, drafting runs, exports) is handed to Celery workers, not done inline in a request handler, so API requests stay fast and the WebSocket/SSE channel can report progress.

## 2. Repo and folder structure conventions

```
backend/
  app/
    main.py            FastAPI app instance, middleware, router mounting
    api/                one module per resource (routers), thin — validation + calling services
    core/               config, security (JWT/RBAC), settings
    models/             SQLAlchemy models (one file per entity or logical group)
    schemas/            Pydantic request/response schemas
    services/           business logic, called from api/ routers
    agents/             LangGraph nodes and graph definition (Phase 4+)
    workers/            Celery tasks
    db/                 session/engine setup, Alembic env
  alembic/              migrations
  tests/                mirrors app/ structure (see docs/testing.md)

frontend/
  src/
    pages/              route-level components
    features/           feature-scoped components + hooks (e.g. questionnaire workspace, knowledge base)
    components/          shared/reusable UI components
    api/                API client functions (fetch/axios wrappers, one module per backend resource)
    hooks/               shared React hooks
    lib/                 utilities
```

Neither folder tree exists in full yet — create subfolders as the phase that needs them is implemented, don't scaffold everything in Phase 0.

## 3. Backend architecture

- **FastAPI** app in `app/main.py`, routers mounted per resource under `app/api/` (e.g. `app/api/auth.py`, `app/api/projects.py`).
- **Pydantic** schemas (`app/schemas/`) for request/response validation, kept separate from **SQLAlchemy** models (`app/models/`) — don't return ORM objects directly from routes.
- **Alembic** manages all schema changes; no hand-edited schema, no `create_all()` in production paths.
- **Auth**: JWT access + refresh tokens (FR-AUTH-01), Google OAuth (FR-AUTH-02). Auth/permission checks live in FastAPI dependencies, not scattered `if` checks in route bodies.
- **RBAC**: role check is a dependency parameterized by required role(s), applied per route. Frontend mirrors the same role table to hide/disable actions, but the API is the actual enforcement point — never trust the frontend to gate access.
- **Business logic** lives in `app/services/`, called by thin route handlers — keeps routes testable and keeps logic out of the HTTP layer.

## 4. Data model

Core entities (client_requirements.md §12). `org_id` on every tenant-scoped table is not optional:

| Entity | Key fields | Introduced |
|---|---|---|
| Organization | id, name, plan, stripe_customer_id, settings (tone, thresholds) | Phase 0 |
| User | id, email, name, auth provider | Phase 0 |
| Membership | user_id, org_id, role | Phase 0 |
| RfpProject | id, org_id, name, buyer, due_date, status, owner_id, source_file | Phase 1 |
| Question | id, project_id, text, section, type, category, position, duplicate_of | Phase 1 |
| Answer | id, question_id, text, choice, confidence, citations, status, assignee, version | Phase 1 |
| AnswerRevision | id, answer_id, text, author (AI/user), created_at | Phase 1/4 |
| KnowledgeDocument | id, org_id, title, s3_key, type, tags, version, status, review_date | Phase 2 |
| KnowledgeChunk | id, document_id, org_id, text, embedding, metadata (page, section) | Phase 2 |
| LibraryAnswer | id, org_id, question, answer, embedding, tags, is_gold, approved_by, source_project | Phase 3 |
| Comment | id, question_id, user_id, body | Phase 4 (fits alongside the fuller review workspace; not in any Phase 1 sub-phase's FR-IDs — see phase-1-llm-basics.md) |
| WorkflowRun | id, project_id, graph_state_ref, status, tokens_used, cost | Phase 4 |
| UsageLedger | id, org_id, credits_delta, reason, created_at | Phase 6 |
| Subscription | id, org_id, stripe_subscription_id, plan, status, period_end | Phase 6 |
| AuditLog | id, org_id, actor, action, entity, timestamp | Phase 0 |
| TenderLead | id, org_id, source, title, summary, fit_score, deadline, url | Phase 7 |

## 5. Frontend architecture

- **Routing**: React Router; route-level components in `src/pages/`.
- **State management (decided in Phase 0.5)**: Redux Toolkit is the single state-management layer — **RTK Query** (`createApi`) for all server/API data (caching, refetch, mutations; replaces an earlier TanStack Query plan), regular slices for client state (auth, current org). `redux-persist` (localStorage engine) persists only the `auth` slice — app code never calls `localStorage` directly. Chosen deliberately over mixing a separate server-state library with ad hoc Context, per the project owner's preference for one state system.
- **Auth transport**: Bearer token in the `Authorization` header (not httpOnly cookies) — the access token is short-lived and the refresh token is DB-tracked/revocable server-side (see backend §3), which bounds the XSS-exposure tradeoff of header-based auth.
- **Styling**: Tailwind CSS. See `docs/ui-ux.md` for component and design-system conventions.
- **Real-time**: a WebSocket/SSE client (Phase 4) drives live drafting progress in the question workspace; falls back to polling only if streaming isn't available in a given environment.

## 6. AI agent pipeline (LangGraph)

Full detail and phased build-out in `docs/phases/phase-4-agents-workflows.md`; this section is the reference architecture once complete.

Nodes: Parser → Classifier → (parallel per question) Retriever → Drafting → Compliance Checker → Router/Supervisor → {auto-approve | Human Review (interrupt) | retry, max 2} → Learning node → Answer Library. See client_requirements.md §7.2 for the full diagram and §7.1 for the tools each node uses.

- **State**: a shared LangGraph state object threaded through all nodes for a given run; checkpointed so a run survives a worker crash or a human-review pause and resumes rather than restarting (FR-AI-10, NFR-03).
- **Provider abstraction**: LLM and embedding calls go through a provider interface, not hardcoded to one vendor — Bedrock, OpenAI, and a local model (Ollama, for dev) must be swappable per environment (FR-AI-11, NFR-11 vendor lock-in mitigation). Build this abstraction starting Phase 1, even though Bedrock itself doesn't land until Phase 5.
- **Grounding rule**: the Drafting Agent may only assert facts backed by a retrieved citation; no citation → "Insufficient information", never a guess (FR-AI-05, §7.3).
- **Prompt-injection defense**: text extracted from uploaded documents is data, never instructions, when constructing prompts — never interpolate raw document text into a system/instruction role (§7.3, FR-AI-12).
- **Prompts**: versioned and centrally stored (not inlined ad hoc per call site), evaluated against a test set before changes are released (§7.3) — see `docs/testing.md` §5.

## 7. Async / background jobs

- **Celery** workers, Redis as broker, for: knowledge base ingestion, drafting runs, exports, scheduled jobs (Phase 7 digests).
- Tasks should be idempotent where possible (especially Stripe webhook handling, FR-BILL-04) and retried on transient failure rather than silently dropped.

## 8. Infrastructure

- **Docker Compose** (repo-root `docker-compose.yml`, `name: bidpilot`) covers local-dev **infra only**: `postgres` (pgvector), `redis`, `minio`. `api` and `web` run natively (`uv run uvicorn app.main:app --reload`, `npm run dev`) rather than in Compose — deliberate, to avoid Docker-Desktop-on-Windows file-watcher overhead slowing down the dev inner loop. Revisit adding `api`/`web` Compose services if/when a prod-like local preview is actually needed.
- **Production target**: AWS (ECS or EC2), S3 for file storage (MinIO is the local stand-in only), Bedrock/Textract/Comprehend for AI services.
- **Config/secrets**: environment variables locally (`.env`, not committed), AWS Secrets Manager in production.
- **CI/CD**: GitHub Actions (Phase 6.7) — lint, test, build; eval suite (Phase 3.6) runs separately, not on every commit, due to LLM cost.

## 9. Cross-cutting concerns

- **Tenant isolation (NFR-05)**: every DB query and every vector search filters by `org_id`. This should be enforced structurally (e.g. a base repository/query helper that requires an org scope) rather than remembered per-query, and covered by explicit cross-tenant-leakage tests (`docs/testing.md`). Zero cross-tenant leakage is an acceptance-level success metric (§14), not a nice-to-have.
- **Observability (NFR-08)**: structured logs, Sentry for errors, Langfuse or LangSmith for LLM tracing, token/cost tracked per request and rolled up per org (Phase 6.4).
- **Cost control (NFR-10)**: per-org token budgets, Redis caching of identical-question responses, cheaper models for cheap steps (e.g. classification vs. drafting).
- **Rate limiting (NFR-07)**: per-user and per-org, via Redis (Phase 6.3).
- **Privacy (NFR-06)**: customer data never used to train models; orgs can delete all their data.

## 10. API conventions

- REST resources under `/api/<resource>`, plural nouns (`/api/projects`, `/api/questions`).
- Errors: consistent JSON error shape (define once in Phase 0/1 and reuse — don't let each router invent its own).
- Pagination: cursor or offset-based, consistent across list endpoints once more than one exists.
- Real-time endpoints (drafting progress) use WebSocket or SSE, documented per-endpoint when built in Phase 4.
