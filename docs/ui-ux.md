# BidPilot UI/UX

Design reference for the frontend. Read the section relevant to what you're building, not the whole file (see `docs/00-INDEX.md`). Nothing here is implemented yet as of Phase 0 — this is the target to build toward, phase by phase (`docs/roadmap.md`).

## 1. Design principles

- **Trust over polish**: this product asks users to trust AI-drafted answers in high-stakes documents (security questionnaires, RFPs). Citations, confidence scores and "who approved this" must always be visible, never hidden behind a click, on any answer.
- **Progress transparency**: drafting a 200-question questionnaire takes minutes, not seconds — the UI must show live progress (per-question status streaming, not a spinner), matching NFR-01/FR-AI-09.
- **Never hide uncertainty**: "Insufficient information" and low-confidence flags are surfaced prominently, not styled to look like a normal complete answer.
- **Accessibility**: WCAG 2.1 AA basics are a baseline requirement (NFR-13), not a later pass — build keyboard nav, contrast and labels in from the start of each screen.

## 2. Navigation / information architecture

Primary sidebar (org-scoped, visible to all roles subject to RBAC hiding items they can't use):

- Dashboard
- Projects (RFP/questionnaire projects list)
- Knowledge Base
- Answer Library
- Analytics
- Settings (org settings, members/roles, billing)

Separate, platform-level: **Super Admin console** (Super Admin role only, not part of the org sidebar — tenants, revenue, cost, error rates).

Org switcher near the top of the sidebar for users belonging to multiple organizations.

## 3. Screens

| Screen | Purpose | Phase introduced |
|---|---|---|
| Login / Signup / Password reset | Auth entry points | 0 |
| Org onboarding | Create org, invite teammates | 0 |
| Dashboard | Active projects, deadlines, automation rate, credits used | 0 (shell) / 6 (real widgets) |
| Project list | All RFP/questionnaire projects, status, deadline | 1 |
| Question mapping / confirmation | Confirm detected questions and column mapping before drafting | 1 |
| **Question workspace** | Core screen: per-question drafting, review, citations, comments | 1 (basic) → 4 (full, live progress) |
| Knowledge base upload/manage | Upload, tag, version documents | 2 |
| Knowledge base search | Semantic + keyword search with previews | 2 |
| Answer Library | Browse/approve/retire/gold library answers | 3 |
| Ask the Knowledge Base (chat) | Free-form cited Q&A | 3 |
| Export | Choose export format, see unapproved-answer warnings | 1 |
| Billing / plan | Stripe Customer Portal entry, usage vs. limit | 6 |
| Analytics | Org + AI-quality + KB-health dashboards | 6 |
| Super Admin console | Tenants, revenue, cost, error rates | 6 |
| Tender Discovery | Profile, matches, digest | 7 |

## 4. Core user flow (the product's spine)

1. **Upload** a questionnaire (Project list → New project → upload file).
2. **Confirm mapping** — user reviews auto-detected questions/columns, corrects mistakes (this step exists specifically because parsing won't be perfect — client_requirements.md §16 risk mitigation).
3. **Drafting runs** — question workspace shows live per-question status (queued → drafting → drafted/needs review) streaming in, not a blocking full-page spinner.
4. **Review** — reviewer works through flagged/all questions: sees draft, citations, confidence, can edit/approve/reject/comment/@mention.
5. **Export** — pick format, see a warning banner if any answers are still unapproved, download the filled file.

Each step maps to FR-IDs in `docs/phases/phase-1-llm-basics.md` (and phase-2/3/4 for the richer drafting behavior) — check there for exact scope per phase before building UI for a capability that doesn't exist yet on the backend.

## 5. Question workspace (detail)

The most complex and most-used screen; gets built incrementally across Phase 1 → 4.

- **Layout**: question list/table on one side (filterable by status, category, confidence, assignee), detail pane for the selected question on the other.
- **List columns**: question text (truncated), category, status badge, confidence badge, assignee.
- **Detail pane**:
  - Question text and detected type.
  - Draft answer text (editable inline).
  - Citation chips (source doc + page/section), clickable to preview the source.
  - Confidence badge (visually distinct thresholds: high/needs-review/insufficient-information — insufficient-information must never look like a normal answer, per §1 above).
  - Status control (approve / reject+comment / re-request with instructions — the last one is FR-AI-07, Phase 4).
  - Comment thread with @mentions.
  - Edit history (AI draft vs. human edits, Phase 4).
- **Bulk actions**: assign by category, bulk-approve above a confidence threshold (only once auto-routing exists, Phase 4).

## 6. Component / design system conventions

- Tailwind CSS utility classes; extract a shared component when a pattern repeats 3+ times, not before.
- Shared components to build once and reuse everywhere they apply: `StatusBadge`, `ConfidenceBadge`, `CitationChip`, `DataTable`, `Modal`, `Toast`, `ProgressStream` (live drafting progress).
- Every screen that lists or shows data needs explicit **loading**, **empty**, and **error** states designed — not just the happy path. Screens gated by role need an explicit **permission-denied** state too (RBAC is enforced server-side, but the UI shouldn't dead-end silently).

## 7. Real-time UX

- Drafting progress (Phase 4) streams over WebSocket/SSE into the question workspace list — per-question status updates live, plus an overall run progress indicator.
- Until Phase 4's streaming lands, Phase 1's synchronous/polled drafting can use a simple progress bar — don't build the full streaming UI early, build it when FR-AI-09 is actually implemented.

## 8. Accessibility checklist (NFR-13, WCAG 2.1 AA basics)

- Full keyboard navigation (tab order, focus visible, no keyboard traps in modals).
- Color contrast meets AA, especially for status/confidence badges (don't rely on color alone — pair with text/icon).
- All form inputs and icon-only buttons have labels (`aria-label` where there's no visible text).
- Focus management on route change and modal open/close.

## 9. Responsive strategy

This is a desktop-first B2B workspace tool (dense tables, side-by-side panes) — optimize for laptop/desktop widths first. Mobile apps are explicitly out of scope for v1 (§5.2), but the web app shouldn't break outright at narrower desktop widths (e.g. a 13" laptop) — collapsing the question list/detail pane into a single-column view at narrow widths is enough; a dedicated mobile layout is not required.
