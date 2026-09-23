# BidPilot Testing Strategy

None of the tooling described below is set up yet as of Phase 0 — this is the target to implement, starting in Phase 0/1 for backend/frontend basics, with AI-specific evaluation added in Phase 3. Set up each tool the first time a phase actually needs it rather than front-loading all of it in Phase 0.

## 1. Coverage target

70%+ line coverage on core backend services is the baseline (NFR-11). Coverage is a floor, not the goal — prioritize tests that would actually catch a regression (tenant isolation, export fidelity, grounding rules) over chasing a percentage.

## 2. Backend testing (pytest)

- Framework: `pytest`, installed as a dev dependency (`uv add --dev pytest pytest-asyncio httpx`).
- Structure: `backend/tests/` mirrors `backend/app/` (e.g. `tests/services/test_projects.py` for `app/services/projects.py`).
- **Run all**: `uv run pytest`
- **Run one file**: `uv run pytest tests/services/test_projects.py`
- **Run one test**: `uv run pytest tests/services/test_projects.py::test_create_project -v`
- **Test database** (settled in Phase 0.2): a dedicated `bidpilot_test` database in the same Compose Postgres container (created by `docker/postgres-init/01-create-test-db.sql`), migrated once per test session, with each test wrapped in a transaction + SAVEPOINT that's rolled back afterward (`join_transaction_mode="create_savepoint"`) — so app-code `commit()` calls during a test are safe without leaking state between tests. See `backend/tests/conftest.py` for the exact fixtures (`apply_migrations`, `engine`, `db_session`, `client`) and reuse them rather than reinventing this per test module. Never test against the dev database.
- **Unit tests**: service-layer logic in isolation (mock external calls — LLM, S3, Stripe).
- **Integration tests**: API routes through FastAPI's test client, hitting the real test database.
- **Tenant isolation tests (mandatory, not optional)**: for every multi-tenant resource, an explicit test that org A cannot read/write org B's data through the API, even with a valid token for org A. This directly backs NFR-05 and the "zero cross-tenant leakage" success metric (client_requirements.md §14). Add this test the same PR a new tenant-scoped resource is added — don't defer it.

## 3. Frontend testing

- Component tests: Vitest + React Testing Library (`npm run test` once configured — add the script when this is set up).
- Test behavior (what the user sees/can do — form validation, status transitions, permission-based hiding), not implementation details (internal state, class names).
- Not every component needs a test; prioritize ones with real logic (forms, status/permission branching) over pure presentational components.

## 4. End-to-end testing

- Tool: Playwright, introduced once there's a real flow worth covering end-to-end (Phase 1 exit criteria: upload → parse → draft → review → export).
- Keep the E2E suite small and focused on the critical path — it's the slowest, most expensive layer; push edge cases down to unit/integration tests instead.

## 5. AI evaluation (distinct from normal tests)

This is not the same as unit/integration testing — it measures answer *quality*, not code correctness, and costs real LLM tokens to run. Introduced in Phase 3.6, used continuously from Phase 4 onward whenever prompts change.

- **Golden dataset**: a fixed set of representative questions with known-good expected answers/sources (can start from public samples — CSA CAIQ, public RFP templates — per client_requirements.md §15 assumption 1).
- **Method**: RAGAS or a custom LLM-as-judge suite.
- **Metrics and targets** (client_requirements.md §14):
  | Metric | Target |
  |---|---|
  | Faithfulness | ≥ 0.85 |
  | Citation accuracy | ≥ 90% |
  | "Insufficient information" correctly returned when no evidence exists | ≥ 95% |
  | Answers approved without edits (on the test dataset) | ≥ 60% |
- **When it runs**: on every prompt/template change before release (§7.3 quality rule), and on a schedule (e.g. nightly) — not on every commit, due to LLM API cost. Wire it as a separate CI job/workflow from the regular test suite, not a step inside it.

## 6. CI pipeline (Phase 6.7)

GitHub Actions: lint (frontend `npm run lint` via oxlint; add a backend linter/formatter when one is chosen — none is picked yet, follow `docs/client_requirements.md` §10's stack rather than adding one ad hoc) → backend tests → frontend tests → build. The AI eval suite (§5 above) runs as a separate, less-frequent workflow, not blocking every PR.

## 7. Manual verification for UI changes

Beyond automated tests, any UI-affecting change should be manually exercised in a running dev server before being called done (per the general "test the golden path in a browser" expectation) — for this app specifically, that means checking at least:
- The change respects RBAC (try it as a role that shouldn't have access).
- Loading/empty/error states render correctly, not just the happy path (`docs/ui-ux.md` §6).
- If it touches the question workspace, confidence/citation/insufficient-information states still render distinctly.
