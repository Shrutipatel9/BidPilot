# Phase 0 — Foundation

**Theme**: Monorepo, Docker Compose (API, web, Postgres, Redis, MinIO), authentication, organizations, role-based access.
**Depends on**: nothing (starting point).
**Read alongside this file**: `docs/architecture.md` §2 (folder structure), §3 (backend), §8 (infra) as each sub-phase needs it.

## Current state

`frontend/` (Vite + React JSX) and `backend/` (FastAPI via `uv`, `app/main.py` with `/` and `/health`) are scaffolded and run locally, but nothing below is built yet: no Docker Compose, no database, no auth, no orgs.

## Sub-phases

### 0.1 Docker Compose local stack
- Services: `api` (FastAPI), `web` (Vite dev server or built frontend), `postgres` (with pgvector extension available for later phases), `redis`, `minio` (S3-compatible storage).
- One-command bring-up: `docker compose up` (NFR-12).
- `.env.example` at repo root (or per-service) documenting required env vars; real `.env` files stay untracked.
- **Exit check**: `docker compose up` gives a running API reachable from the host and a Postgres instance the API can connect to.

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
- **Read**: `docs/ui-ux.md` §2 (navigation) and §3 (screen list) before building this.

## Exit criteria — demo

A user can: sign up, verify email, log in, create an organization, invite a teammate with a role, and see that role's permissions reflected in the UI. Two different organizations' data is provably isolated (manually verified here; automated isolation tests land in Phase 1+ per `docs/testing.md`).
