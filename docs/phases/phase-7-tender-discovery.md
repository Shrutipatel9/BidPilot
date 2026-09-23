# Phase 7 — Tender Discovery Agent (Bonus, optional)

**Theme**: Tool-using autonomous agent that discovers external tenders/RFPs matching the org's profile, with scheduled digests.
**Depends on**: Phase 6 (product is otherwise production-ready; this is an additive feature).
**Read alongside this file**: `docs/architecture.md` §6 (agent pattern — this reuses the tool-using-agent shape, not the review/checkpoint machinery from Phase 4).

Explicitly optional per client_requirements.md §5.1/§13 — confirm with the user before starting this phase.

## Sub-phases

### 7.1 Org tender profile
- Org defines: services, industries, locations, contract size range, certifications.
- **FR**: FR-TND-01.

### 7.2 Tender Scout Agent
- Tool-using agent searches permitted sources only (public APIs, RSS feeds, allowed web search) — terms-of-service compliance is a hard constraint, not a nice-to-have.
- **FR**: FR-TND-02, FR-TND-06.

### 7.3 Fit scoring and summary
- Each match: fit score, summary, eligibility criteria, deadline, required documents.
- `TenderLead` entity.
- **FR**: FR-TND-03.

### 7.4 Convert to RFP project
- One click turns a discovered tender into an `RfpProject`, feeding into the Phase 1-4 pipeline.
- **FR**: FR-TND-04.

### 7.5 Scheduled digest
- Daily digest by email or in-app of new matches.
- **FR**: FR-TND-05.

## Exit criteria — demo

With a tender profile configured, the agent surfaces at least one plausible match from an allowed source with a fit score and summary, and converting it produces a working RFP project ready to run through drafting.
