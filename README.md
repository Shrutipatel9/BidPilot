# BidPilot

AI copilot for RFPs, RFIs, and security/compliance questionnaires. A user uploads a questionnaire (Excel/Word/PDF), BidPilot drafts grounded, cited answers from the org's knowledge base via a multi-agent (LangGraph) workflow, routes low-confidence answers to human reviewers, and exports the finished response in the original file format.

Full product spec: [`docs/client_requirements.md`](docs/client_requirements.md). MVP scope and delivery roadmap: [`docs/mvp.md`](docs/mvp.md) and [`docs/roadmap.md`](docs/roadmap.md).

## For Claude Code / contributors

Start with [`CLAUDE.md`](CLAUDE.md), then [`docs/00-INDEX.md`](docs/00-INDEX.md) — the map of everything in `docs/` and what to read for a given task.

## Project layout

- `frontend/` — React (JSX) SPA, built with Vite
- `backend/` — Python FastAPI service, managed with `uv`
- `docs/` — product spec, architecture, UI/UX, testing strategy, and the phased roadmap

## Running locally

```
# backend
cd backend
uv sync
uv run uvicorn app.main:app --reload   # http://localhost:8000

# frontend
cd frontend
npm install
npm run dev                             # http://localhost:5173
```

A Docker Compose stack (Postgres, Redis, MinIO, api, web) is planned for Phase 0.1 — see [`docs/phases/phase-0-foundation.md`](docs/phases/phase-0-foundation.md).

## Status

Early scaffold stage (Phase 0 of the roadmap). See [`docs/roadmap.md`](docs/roadmap.md) for what's built vs. planned.
