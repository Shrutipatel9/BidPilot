# BidPilot UI/UX

Design reference for the frontend. Read the section relevant to what you're building, not the whole file (see `docs/00-INDEX.md`). §2 (visual identity) and §7 (component library) are implemented as of Phase 0.5 — treat them as binding, not aspirational. Everything screen/feature-specific beyond the auth/org/settings screens already built is still the target to build toward, phase by phase (`docs/roadmap.md`).

## 1. Design principles

- **Professional execution, not scaffolding.** This is a paid B2B tool selling trust — it must never look like an unstyled framework default (a centered white box on a blank page, native `<select>` chevrons, plain-text "Loading…"). Every screen ships with real visual design: hierarchy, spacing, icons, feedback states. §2 below is not optional polish, it's the baseline.
- **Trust over polish**: this product asks users to trust AI-drafted answers in high-stakes documents (security questionnaires, RFPs). Citations, confidence scores and "who approved this" must always be visible, never hidden behind a click, on any answer.
- **Progress transparency**: drafting a 200-question questionnaire takes minutes, not seconds — the UI must show live progress (per-question status streaming, not a spinner), matching NFR-01/FR-AI-09.
- **Never hide uncertainty**: "Insufficient information" and low-confidence flags are surfaced prominently, not styled to look like a normal complete answer.
- **Every action gives visible feedback.** A successful mutation must always produce something the user can see — a redirect, a success `Callout`, an updated list row. A debug-only signal (e.g. Phase 0's dev-mode `debug_link`) is never the *only* feedback a real user path relies on; that was a real bug caught in Phase 0.5 (invite succeeded silently once real SMTP was configured because only the dev-mode debug link was shown) — don't reintroduce it elsewhere.
- **Accessibility**: WCAG 2.1 AA basics are a baseline requirement (NFR-13), not a later pass — build keyboard nav, contrast and labels in from the start of each screen.

## 2. Visual identity and design tokens

Established in Phase 0.5 (`frontend/src/index.css`, Tailwind v4 CSS-first `@theme`). Treat these as fixed unless the project owner asks to rebrand — don't introduce a second color/type system in a later phase.

- **Typeface**: Inter, loaded via Google Fonts (`index.html`) and set as `--font-sans` in `@theme`, so plain Tailwind `font-sans` (the default) already resolves to it — no per-component font class needed.
- **Color — `brand`**: a custom Tailwind color namespace (`--color-brand-50…950` in `index.css`, currently an indigo scale) used as `bg-brand-600`, `text-brand-700`, `ring-brand-500/15`, etc. It's aliased rather than using Tailwind's stock `indigo-*` directly so the whole palette can be swapped in one file later without touching every component.
- **Color — neutral**: Tailwind's `slate-*` scale for text/borders/backgrounds (slate reads cooler/more professional than plain `gray-*` — don't mix the two).
- **Color — semantic**: `emerald-*` for success, `rose-*` for danger/errors, `amber-*` for warning, plus `sky-*`/`violet-*` as auxiliary categorical accents (used by `RoleBadge` to distinguish role tiers). Never rely on color alone — pair with an icon or label (also an accessibility requirement, §9).
- **Elevation**: `border border-slate-200` + `shadow-sm` on cards — never a heavy/dark drop shadow. Interactive elements get a `focus:ring-4 ring-{color}/15` glow, not just a border-color change, so keyboard focus is unmistakable.
- **Radius**: `rounded-lg` (buttons, inputs, small cards) / `rounded-xl` (page-level containers) / `rounded-full` (badges, avatars, pills) — pick from these three, don't invent a fourth.
- **Spacing**: generous by default — `px-3.5 py-2.5` on inputs/buttons, `p-5` inside card sections, `p-8` page padding in the app shell's `<main>`. A cramped "form crammed in a box" layout is exactly what §1 forbids.
- **Icons**: `lucide-react` exclusively (`size-4` inline with text, `size-7`/`size-8` for avatar/logo marks) — never mix in another icon set or raw inline SVGs for the same kind of UI element.
- **Native form controls**: browser-default `<select>` styling is overridden globally (`index.css`) with a custom chevron matching the palette — don't let a raw unstyled native control ship into a screen.

## 3. Navigation / information architecture

Primary sidebar (org-scoped, visible to all roles subject to RBAC hiding items they can't use):

- Dashboard
- Projects (RFP/questionnaire projects list)
- Knowledge Base
- Answer Library
- Analytics
- Settings (org settings, members/roles, billing)

Separate, platform-level: **Super Admin console** (Super Admin role only, not part of the org sidebar — tenants, revenue, cost, error rates).

Org switcher near the top of the sidebar for users belonging to multiple organizations.

## 4. Screens

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

## 5. Core user flow (the product's spine)

1. **Upload** a questionnaire (Project list → New project → upload file).
2. **Confirm mapping** — user reviews auto-detected questions/columns, corrects mistakes (this step exists specifically because parsing won't be perfect — client_requirements.md §16 risk mitigation).
3. **Drafting runs** — question workspace shows live per-question status (queued → drafting → drafted/needs review) streaming in, not a blocking full-page spinner.
4. **Review** — reviewer works through flagged/all questions: sees draft, citations, confidence, can edit/approve/reject/comment/@mention.
5. **Export** — pick format, see a warning banner if any answers are still unapproved, download the filled file.

Each step maps to FR-IDs in `docs/phases/phase-1-llm-basics.md` (and phase-2/3/4 for the richer drafting behavior) — check there for exact scope per phase before building UI for a capability that doesn't exist yet on the backend.

## 6. Question workspace (detail)

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

## 7. Component / design system conventions

Tailwind CSS utility classes; extract a shared component when a pattern repeats 3+ times, not before. §2's tokens are the only source of color/spacing/radius values — don't hardcode a one-off hex or px value in a component.

**Built (Phase 0.5, `frontend/src/components/`)** — reuse these, don't recreate their styling ad hoc in a page:
- `Logo` — the wordmark, with a `light` variant for use on the brand-colored auth panel.
- `RoleBadge` (`components/RoleBadge.jsx`) — color-coded pill per membership role (`lib/roles.js` holds the label map). This is the pattern for any future status/category badge: a small style-map object keyed by the enum value, one shared component, never inline conditional classes at the call site.
- `form/Button` — `variant` (`primary`/`secondary`/`ghost`), `loading` (shows a spinner, auto-disables), and a polymorphic `as` prop (e.g. `as={Link}`) so a nav-styled-as-a-button control still goes through one definition instead of a hand-styled `<Link>`.
- `form/TextInput` — label + input, optional `labelExtra` (e.g. an inline "Forgot password?" link next to the label) and `hint` (helper text below).
- `form/ErrorBanner` — renders an RTK Query error object (`error.data.detail`) as an icon-led red banner; pass it the mutation/query's `error` directly.
- `form/Callout` — `info`/`success` icon-led banner, for anything that isn't strictly an error (dev-mode debug links, success confirmations — see §1's "every action gives visible feedback").
- `form/AuthCard` — the split-screen layout for every unauthenticated page (signup, login, password reset, accept-invitation, create-organization): brand gradient + value-prop copy on the left (desktop only), the form on the right. Don't build a new centered-box layout for another auth-style page — extend this one.
- `layout/AppShell` — the authenticated app frame: fixed sidebar (nav with icons, "Soon" badges on not-yet-built sections, org switcher, avatar+email+logout footer) and a scrollable `<main>`. New authenticated pages are routed as children of this, not given their own layout.
- `StatusBadge`/`ConfidenceBadge` (Phase 1.4, `components/`) — same style-map pattern as `RoleBadge`, for `Answer.status` and confidence thresholds (emerald ≥80, amber 50-79, rose <50) in the question review pane.
- `CitationChip` (Phase 2.6, `components/CitationChip.jsx`) — document title + page/section, click toggles an inline snippet preview from the citation's own `snippet` field (no extra request). Shared by the review pane's citation list and the knowledge base search results.
- `DocumentStatusBadge` (Phase 2.1, `components/`) — same pattern again, for `KnowledgeDocument.status`.

**Still to build** (later phases, once the underlying feature exists — don't build the component before the data it displays exists): `DataTable` (generalize `SettingsMembersPage`'s list once a second dense table appears — e.g. the question workspace list), `Modal`, `Toast`, `ProgressStream` (live drafting progress, Phase 4).

Every screen that lists or shows data needs explicit **loading**, **empty**, and **error** states designed — not just the happy path. Screens gated by role need an explicit **permission-denied** state too (RBAC is enforced server-side, but the UI shouldn't dead-end silently).

## 8. Real-time UX

- Drafting progress (Phase 4) streams over WebSocket/SSE into the question workspace list — per-question status updates live, plus an overall run progress indicator.
- Until Phase 4's streaming lands, Phase 1's synchronous/polled drafting can use a simple progress bar — don't build the full streaming UI early, build it when FR-AI-09 is actually implemented.

## 9. Accessibility checklist (NFR-13, WCAG 2.1 AA basics)

- Full keyboard navigation (tab order, focus visible, no keyboard traps in modals).
- Color contrast meets AA, especially for status/confidence badges (don't rely on color alone — pair with text/icon).
- All form inputs and icon-only buttons have labels (`aria-label` where there's no visible text).
- Focus management on route change and modal open/close.

## 10. Responsive strategy

This is a desktop-first B2B workspace tool (dense tables, side-by-side panes) — optimize for laptop/desktop widths first. Mobile apps are explicitly out of scope for v1 (§5.2), but the web app shouldn't break outright at narrower desktop widths (e.g. a 13" laptop) — collapsing the question list/detail pane into a single-column view at narrow widths is enough; a dedicated mobile layout is not required.
