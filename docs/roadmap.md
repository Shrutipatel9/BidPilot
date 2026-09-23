# BidPilot Delivery Roadmap

**MVP is Phases 0-2** — see `docs/mvp.md` for what that means and why. Phases 3-7 below are the full learning-driven roadmap and are post-MVP; don't start them without checking `mvp.md` first.

Master phase index. This file is a **map, not the detail** — each phase's tasks, acceptance criteria and FR-ID traceability live in `docs/phases/phase-N-*.md`. Read only the phase file you're currently working on; don't load all of them at once (see `docs/00-INDEX.md`).

Phases are sequential and each must end with a **working, demo-able product increment** (client_requirements.md §13). Do not start a later phase's sub-phase until the prior phase's exit criteria are met, unless the user explicitly asks to jump ahead.

## Phase list

| Phase | Theme | File | Depends on | Primary concepts learned |
|---|---|---|---|---|
| 0 | Foundation | [phase-0-foundation.md](phases/phase-0-foundation.md) | — | Production project setup |
| 1 | LLM basics (no RAG) | [phase-1-llm-basics.md](phases/phase-1-llm-basics.md) | 0 | Prompt engineering, structured output |
| 2 | RAG | [phase-2-rag.md](phases/phase-2-rag.md) | 1 | Embeddings, vector DB, RAG |
| 3 | Advanced RAG | [phase-3-advanced-rag.md](phases/phase-3-advanced-rag.md) | 2 | LangChain, RAG evaluation |
| 4 | Agents and workflows | [phase-4-agents-workflows.md](phases/phase-4-agents-workflows.md) | 3 | LangGraph, AI agents, AI workflows |
| 5 | AWS AI | [phase-5-aws-ai.md](phases/phase-5-aws-ai.md) | 4 | AWS AI services |
| 6 | Production and SaaS | [phase-6-production-saas.md](phases/phase-6-production-saas.md) | 4 (5 optional) | Production engineering |
| 7 | Bonus: Tender Discovery | [phase-7-tender-discovery.md](phases/phase-7-tender-discovery.md) | 6 | Tool-using autonomous agents |

Phase 5 (AWS AI) can run in parallel with / after Phase 4 rather than strictly before Phase 6, since Bedrock is a swappable LLM provider (NFR-11 vendor lock-in mitigation) — the pipeline built in Phase 4 should already be provider-agnostic. Treat the "Depends on" column as the recommended order, not a hard technical block, and confirm with the user before reordering.

## Sub-phase numbering

Each phase file breaks its theme into sub-phases numbered `N.1`, `N.2`, ... in build order. A sub-phase is the right size for a single focused implementation session (roughly one PR). If a sub-phase turns out to still be too large while implementing it, split it further (`N.1a`/`N.1b` or `N.1.1`) in that phase file rather than starting undocumented work.

## Cross-phase conventions

- **Traceability**: every sub-phase lists the `FR-*`/`NFR-*` IDs it implements, from `docs/client_requirements.md` §6/§8. If a task doesn't map to an ID, check it's actually in scope before building it.
- **Definition of done** for a sub-phase: code + tests (see `docs/testing.md`) + it works end-to-end in a manual run, not just unit-tested in isolation.
- **Definition of done** for a phase: all its sub-phases done, plus the phase's own "Exit criteria — demo" section in its file.
- Scope changes go in `docs/client_requirements.md` first (per that file's header), then get reflected here.
