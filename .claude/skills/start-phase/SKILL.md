---
name: start-phase
description: Load the minimum set of BidPilot docs needed to begin implementing a roadmap phase or sub-phase (e.g. "1.2"), following docs/00-INDEX.md's reading order, then summarize scope before writing code. Use when the user says "start phase X", "implement sub-phase X.Y", "let's build phase X", "what's next on the roadmap", or similar.
---

# Start Phase

Begin work on a BidPilot roadmap phase/sub-phase without loading the whole `docs/` tree into context. This exists because `docs/client_requirements.md` and the architecture/UI-UX/testing docs are large — most sessions only need a small slice of them.

## Steps

1. **Identify the target phase/sub-phase.**
   - If the user named one (e.g. "1.2", "phase 3"), use it directly.
   - If they said "what's next" or didn't name one, read `docs/roadmap.md` (small file) to find the phase order, then check the repo's current state (what's actually implemented — look at `backend/app/` and `frontend/src/`, not just docs) against `docs/phases/phase-N-*.md` exit criteria to find the next unimplemented sub-phase. If it's genuinely ambiguous, ask the user rather than guessing.
   - If the target is Phase 3 or later, read `docs/mvp.md` first — that work is explicitly post-MVP. If MVP (Phases 0-2) isn't fully done yet, flag that and confirm the user actually wants to jump ahead rather than assuming it.

2. **Read the phase file**: `docs/phases/phase-N-*.md` in full (these are short — 30-60 lines). This gives the sub-phase's scope, FR-ID traceability, and the phase's exit criteria.

3. **Read only the matching sections** of the other docs, based on what the sub-phase actually touches — don't read a whole file when one `§` covers it:
   - Backend/API/data model work → `docs/architecture.md` §2 (folders), §3 (backend), §4 (data model), §9 (tenant isolation — always, it's non-negotiable) → `docs/testing.md` §2.
   - Frontend/screen work → `docs/ui-ux.md` (the relevant screen from its §3 table, then that section) → `docs/architecture.md` §5 → `docs/testing.md` §3.
   - LangGraph/agent work → `docs/architecture.md` §6 (+ `docs/phases/phase-4-agents-workflows.md` if not already the current phase file) → `docs/testing.md` §5.
   - Infra/DevOps → `docs/architecture.md` §8 → `docs/testing.md` §6.
   - Billing/Stripe → `docs/architecture.md` §9 (idempotency note).
   - **Do not** read `docs/client_requirements.md` in full. Only pull a specific section from it if the phase file leaves a genuine scope ambiguity (e.g. exact wording of one `FR-*` requirement).

4. **Plan and state it**: state the sub-phase's goal, the FR-IDs in play, its exit criteria, and your concrete implementation plan back to the user in a few sentences. This is a checkpoint, not a formality — it's where a wrong phase/scope guess gets caught before code is written.

5. **Ask open questions, if any**: before implementing, check whether the sub-phase or plan leaves a real ambiguity — a design choice only the user can make, a decision the docs don't cover, conflicting requirements, or a needed env var/API key/credential (see below). If so, ask now (e.g. with `AskUserQuestion`) rather than guessing. If the docs already answer it, don't ask — that's what step 3 was for. If nothing's ambiguous, say so briefly and move on; don't manufacture questions.

   - **Env vars / secrets checkpoint**: if the plan needs a new environment variable, API key, or credential (AWS, Bedrock, Stripe, OpenAI, Google OAuth, SMTP, a database URL pointing at a real external service, etc.), stop here and ask the user for it — never invent a placeholder that would silently no-op or fail later, and never pick a provider/account unilaterally. Explain concretely how/where to obtain it (the specific console, page, and steps — not just "get an API key"). Add the variable to the relevant `.env.example` with a comment on what it's for; real values only ever go in untracked `.env` files. Flag it plainly if the service is paid/metered so the user isn't surprised by cost.

6. **Implement** the plan, following the conventions already read (folder structure, tenant-isolation rule, grounding/citation rule if AI-facing, etc.) and anything in the repo's `CLAUDE.md`.

7. **Test properly** before calling it done — per `docs/testing.md` for the layer touched: backend changes get pytest coverage, including the mandatory tenant-isolation test for any new tenant-scoped resource; frontend changes get component tests plus a manual run in the dev server; AI-facing changes get checked against the grounding/citation rule, not just "it runs." "It compiles" is not "it's tested" — don't skip this step even for a small sub-phase.

8. **On completion**, check the sub-phase's own exit criteria (and the phase file's overall "Exit criteria — demo" if this was the last sub-phase in the phase) against what was actually built and tested, and say plainly what's done vs. still open.
