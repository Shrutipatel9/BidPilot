# Documentation Map

Read this file first when you need to orient in `docs/`. It exists so you read the *minimum* set of files for the task at hand instead of loading the whole `docs/` tree — `client_requirements.md` alone is ~460 lines and the phase files below already extract what most tasks need from it.

## What's in `docs/`

| File | What it's for | Size |
|---|---|---|
| `client_requirements.md` | Full product spec, source of truth for scope. Has every `FR-*`/`NFR-*` ID. | Large (~460 lines) |
| `mvp.md` | What counts as MVP (through Phase 2) vs. post-MVP, and why. Read before deciding to start Phase 3+ work. | Small |
| `roadmap.md` | Phase list + links + cross-phase conventions. Not the detail. | Small |
| `phases/phase-N-*.md` | One file per phase, with `N.1`/`N.2` sub-phases, FR-ID traceability, exit criteria. | Small each |
| `architecture.md` | Target system architecture: folder layout, backend/frontend structure, data model, agent pipeline, infra, cross-cutting rules. Sectioned — read one `§` at a time. | Medium |
| `ui-ux.md` | Screens, navigation, core user flow, question-workspace detail, component conventions, accessibility. Sectioned. | Medium |
| `testing.md` | Test strategy per layer (backend/frontend/E2E/AI eval), how to run each, coverage target. Sectioned. | Medium |

## Reading order by task type

Don't read a file's full contents when only one section is relevant — `architecture.md`, `ui-ux.md`, and `testing.md` are numbered so you can jump straight to the `§` named below.

**Starting any implementation task** (do this first, always):
1. `roadmap.md` — find which phase the task belongs to.
2. The matching `phases/phase-N-*.md` — get the sub-phase's FR-IDs, scope, and exit criteria.
3. If the task is in Phase 3 or later, check `mvp.md` first — that work is explicitly post-MVP; confirm with the user before pulling it forward rather than assuming it's next.

Then, depending on what you're touching:

- **Backend feature (API/service/model)**: `architecture.md` §2 (folders), §3 (backend), §4 (data model for the entities involved), §9 (tenant isolation — always) → `testing.md` §2 (backend tests + mandatory isolation test).
- **Frontend feature (screen/component)**: `ui-ux.md` for the relevant screen (§3 finds it, then the specific section) → `architecture.md` §5 (frontend conventions) → `testing.md` §3.
- **LangGraph / agent work**: `architecture.md` §6 → the phase file (almost always `phase-4-agents-workflows.md`) → only if you need the original narrative/diagram, `client_requirements.md` §7 → `testing.md` §5 (AI eval, not regular tests).
- **Data model change**: `architecture.md` §4, then check every phase file that references the entity so sub-phase scope stays consistent.
- **Infra/DevOps (Docker, CI, deploy)**: `architecture.md` §8 → `testing.md` §6.
- **Billing/Stripe**: `phase-6-production-saas.md` §6.1/6.2 → `architecture.md` §9 (idempotency note).
- **A genuine scope question** ("is X actually in v1?", "what does FR-AI-05 require exactly?"): go straight to `client_requirements.md` — the phase files summarize it but aren't a substitute for the source of truth on ambiguous scope calls.

## When to update these docs

- Scope change → `client_requirements.md` first (per its own header), then reflect it in the relevant phase file.
- Architectural decision made while implementing (e.g. how the provider abstraction ended up shaped) → `architecture.md`, same PR.
- New screen/flow designed while implementing → `ui-ux.md`, same PR.
- A phase's scope turns out wrong once you're in it → edit that phase file directly; don't let the doc drift from reality.
