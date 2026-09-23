# MVP Definition

**MVP = through the end of Phase 2** (`docs/phases/phase-0-foundation.md`, `phase-1-llm-basics.md`, `phase-2-rag.md`). Confirmed with the project owner 2026-09-23.

## Why this boundary

Phase 2's exit criteria already deliver the core business problem this product exists to solve (client_requirements.md §2/§3.1): upload a questionnaire, get AI drafts grounded in the org's own knowledge base with visible citations and confidence scores, have a person review/approve them, and export in the original format. That's a usable, demoable product — not a toy. Phases 3+ make it better (advanced retrieval, full agent orchestration, AWS AI, billing, tender discovery) but the product already does its job without them.

## What's in the MVP

| Phase | Contributes |
|---|---|
| 0 — Foundation | Auth, orgs, RBAC, tenant isolation — nothing works multi-tenant-safely without this |
| 1 — LLM basics | Upload → parse → draft (no grounding yet) → review → export: the end-to-end shape |
| 2 — RAG | Turns Phase 1's drafts into grounded, cited, confidence-scored answers — the part that actually makes answers trustworthy |

Everything a Phase 0-2 sub-phase needs (its FR-IDs, scope, exit criteria) is already detailed in the respective phase file — this doc doesn't duplicate that, it just draws the line.

## What's explicitly post-MVP (build only when asked, or once MVP is stable and the owner wants to continue)

- **Phase 3** (hybrid search/re-ranking, Answer Library, Ask-the-KB chat, eval suite) — quality/scale improvements on top of a working RAG pipeline.
- **Phase 4** (LangGraph orchestration, compliance checker, human-review interrupts, parallel execution) — Phase 1-2 can ship with a simpler synchronous/sequential drafting flow; formal LangGraph orchestration is a maturity upgrade, not required for the core value prop.
- **Phase 5** (Bedrock/Textract/Comprehend/Guardrails) — a provider swap and scanned-document support; OpenAI/local-model + non-scanned files are enough for MVP.
- **Phase 6** (Stripe billing, rate limiting, analytics, observability, CI/CD, AWS deploy) — needed before charging real customers or running unattended in production, not before proving the product works.
- **Phase 7** (Tender Discovery) — explicitly optional/bonus even in the full roadmap.

## Implication for how work gets prioritized

When there's a choice between polishing something inside Phase 0-2 further vs. starting Phase 3+, default to finishing MVP scope first unless the project owner says otherwise. Don't pull forward Phase 3+ complexity (hybrid search, LangGraph, Bedrock, billing) into MVP work "for completeness" — that's scope creep against an explicit decision, not thoroughness.

If this boundary changes, update this file and say so — don't let `docs/roadmap.md`'s phase order silently imply a different MVP than what's recorded here.
