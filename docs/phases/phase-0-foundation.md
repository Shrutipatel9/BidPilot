# Phase 0 — Foundation

**Theme**: Monorepo, Docker Compose (API, web, Postgres, Redis, MinIO), authentication, organizations, role-based access.
**Depends on**: nothing (starting point).
**Read alongside this file**: `docs/architecture.md` §2 (folder structure), §3 (backend), §8 (infra) as each sub-phase needs it.

## Current state

`frontend/` (Vite + React JSX) and `backend/` (FastAPI via `uv`, `app/main.py` with `/` and `/health`) are scaffolded and run locally, but nothing below is built yet: no Docker Compose, no database, no auth, no orgs.

## Sub-phases

### 0.1 Docker Compose local stack
- Services: `postgres` (pgvector-enabled, `pgvector/pgvector:pg16`), `redis`, `minio` (S3-compatible storage). **`api` and `web` deliberately run natively** (`uv run uvicorn app.main:app --reload`, `npm run dev`), not in Compose — avoids Docker-Desktop-on-Windows bind-mount/file-watcher slowness for the dev inner loop. A `web`/`api` Compose service can be added later for a prod-like preview if needed; NFR-12's "one-command setup" is satisfied for the infra dependencies, not the app processes themselves, at this stage.
- `docker-compose.yml` lives at the repo root (not inside `backend/`) with an explicit `name: bidpilot`, so its container/network names never collide with an unrelated project.
- A Postgres init script creates a separate `bidpilot_test` database (used by the backend test suite, `docs/testing.md` §2) and enables the `vector` extension in both databases, alongside `.env.example` files (root-adjacent, per-service) documenting required env vars; real `.env` files stay untracked.
- **Exit check**: `docker compose up -d` brings up postgres/redis/minio healthy, and `uv run uvicorn app.main:app --reload` (run natively) connects to the Dockerized Postgres successfully.

### 0.2 Database and migrations
- Add SQLAlchemy + Alembic to `backend`.
- Base models: `Organization`, `User`, `Membership` (see `docs/architecture.md` §4 for the full target entity list — only these three are needed now).
- Alembic migration workflow documented (how to generate/apply a migration) in `docs/testing.md`'s backend section or a short note here once set up.
- **FR/NFR**: none directly; infrastructure for FR-AUTH-*.

### 0.3 Authentication
- Email + password signup/login with JWT access + refresh tokens.
- Google OAuth login.
- Email verification and password reset flows.
- **FR**: FR-AUTH-01, FR-AUTH-02, FR-AUTH-03.

### 0.4 Organizations and RBAC
- Create organization; invite members by email with a role.
- Roles: Owner, Admin, Knowledge Manager, Responder, Reviewer (SME), Viewer (client_requirements.md §4.2) — plus the platform-level Super Admin (§4.3, not org-scoped).
- RBAC enforced in the API (dependency/middleware layer) and mirrored in the frontend (hide/disable actions the current role can't perform).
- Tenant isolation: every table from 0.2 onward carries `org_id`; every query filters by it. This is the one rule that must never regress — see `docs/architecture.md` §9.
- Audit log of logins, approvals, exports, deletions, role changes.
- **FR**: FR-AUTH-04, FR-AUTH-05, FR-AUTH-06, FR-AUTH-07.

### 0.5 Base frontend shell
- Routing (React Router), auth pages (login/signup/reset), protected-route wrapper, org context/switcher.
- Empty-state dashboard shell to land on after login (real widgets come in later phases).
- **Read**: `docs/ui-ux.md` §2 (visual identity/design tokens), §3 (navigation) and §4 (screen list) before building this.

## Exit criteria — demo

A user can: sign up, verify email, log in, create an organization, invite a teammate with a role, and see that role's permissions reflected in the UI. Two different organizations' data is provably isolated (manually verified here; automated isolation tests land in Phase 1+ per `docs/testing.md`).
