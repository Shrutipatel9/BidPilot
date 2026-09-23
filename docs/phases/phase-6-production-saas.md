# Phase 6 — Production and SaaS

**Theme**: Stripe billing and credits, Redis rate limits and caching, analytics, observability, cost tracking, CI/CD, AWS deploy.
**Depends on**: Phase 4 (core product complete enough to sell/operate). Can run alongside or after Phase 5.
**Read alongside this file**: `docs/architecture.md` §8 (infra), §9 (cross-cutting: observability/caching/rate-limiting).

## Sub-phases

### 6.1 Stripe billing core
- Stripe Checkout for subscriptions; Stripe Customer Portal for plan changes/invoices/payment methods.
- Webhooks kept idempotent (safe to receive twice) and keep subscription status in sync.
- **FR**: FR-BILL-01, FR-BILL-04.

### 6.2 Credits and usage
- Usage tracked in credits (1 drafted question = 1 credit); `UsageLedger` entity.
- One-time top-up packs; 14-day trial with limited credits.
- Soft warning at 80% usage, hard block at 100% with an upgrade button.
- **FR**: FR-BILL-02, FR-BILL-03, FR-BILL-05, FR-BILL-06.

### 6.3 Redis rate limiting and caching
- Per-user and per-org API rate limits.
- Cache identical-question responses to cut redundant LLM calls.
- **NFR**: NFR-07, NFR-10 (caching half; token-budget half is 6.4).

### 6.4 Observability and cost tracking
- Structured logging, Sentry error tracking, Langfuse/LangSmith LLM tracing, token/cost tracking per request and per org.
- Per-org token budgets (completes NFR-10 with 6.3's caching).
- **NFR**: NFR-08, NFR-10.

### 6.5 Analytics dashboards
- Org dashboard: active projects, deadlines, automation rate, time saved, credits used.
- AI quality metrics: average confidence, approval-without-edits rate, most-edited categories.
- Knowledge base health: stale documents, question gaps with no good source.
- Super Admin dashboard: tenants, revenue, LLM token cost per tenant, error rates.
- **FR**: FR-ANL-01, FR-ANL-02, FR-ANL-03, FR-ANL-04.

### 6.6 Notifications
- In-app and email notifications: assignments, mentions, approaching due dates, completed drafting runs.
- **FR**: FR-REV-06.

### 6.7 CI/CD and deployment
- GitHub Actions CI (lint, tests, build).
- Containerize fully with Docker; deploy target AWS (ECS or EC2).
- **NFR**: NFR-12.

## Exit criteria — demo

A new org can sign up, hit its trial credit limit and see the upgrade prompt, subscribe via Stripe Checkout, and see usage/cost reflected on its dashboard and the Super Admin dashboard. A deploy runs through CI/CD to AWS. Error tracking and LLM cost-per-request are visible in the observability stack, not just in logs.
