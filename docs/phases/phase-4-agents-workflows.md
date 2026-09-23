# Phase 4 — Agents and Workflows

**Theme**: LangGraph multi-agent pipeline, compliance checker, human review, checkpoints, parallel execution, real-time progress.
**Depends on**: Phase 3 (Retriever/Drafting/Answer Library all exist as functions — this phase formalizes them into a LangGraph graph and adds the remaining agents).
**Read alongside this file**: `docs/architecture.md` §6 (full agent pipeline architecture), client_requirements.md §7 (agent responsibilities + workflow diagram) — this is the one phase where reading §7 in full is worth it.

This is the architecturally central phase: it turns the linear pipeline from Phases 1-3 into the stateful, resumable, human-in-the-loop LangGraph workflow described in client_requirements.md §7.2.

## Sub-phases

### 4.1 LangGraph state and graph definition
- Define the shared workflow state schema and wire existing Parser → Retriever → Drafting logic as graph nodes.
- **FR**: FR-AI-01.

### 4.2 Classifier Agent
- Categorize each question (Security, Privacy, Legal, Product, Commercial, ...) and difficulty; integrate duplicate removal (built in 3.4) as part of this node.
- **FR**: FR-RFP-05.

### 4.3 Compliance Checker Agent
- LLM-as-judge pass: check drafts agree with policy documents and with each other (e.g. consistent encryption answer everywhere in the same run).
- **FR**: FR-AI-13.

### 4.4 Router/Supervisor and confidence thresholds
- Rules + LLM decision: auto-approve, send to human review, or retry (max 2 retries).
- Confidence threshold config (org-level) drives auto-routing.
- **FR**: FR-REV-02.

### 4.5 Human review interrupt/resume
- LangGraph interrupt at the Human Review node; workflow resumes on reviewer action.
- Reviewer can edit/approve/reject with a comment; rejection triggers AI re-draft using the feedback.
- Full edit history (AI draft vs. human edits).
- **FR**: FR-AI-10, FR-REV-03, FR-REV-04.

### 4.6 Parallel batches and real-time progress
- Run question batches in parallel; stream progress to the UI via WebSocket/SSE.
- Checkpointing so a run resumes after a crash, not just after a review pause.
- **FR**: FR-AI-09, FR-AI-10 (completes it). **NFR**: NFR-01 (200 questions < 10 min), NFR-03 (resumable after crash).

### 4.7 Learning node
- On approval, auto-promote to the Answer Library (building on 3.3's manual promotion) with embeddings.
- **FR**: FR-REV-05 (automation of the loop).

### 4.8 Regenerate with instructions
- Re-generate a single answer with user instructions ("shorter", "more formal", "mention ISO 27001").
- **FR**: FR-AI-07.

## Exit criteria — demo

Run a full questionnaire through the graph: parallel drafting with live progress, a low-confidence answer pauses for human review and resumes correctly after approval, a rejected answer gets a feedback-driven re-draft, a compliance conflict gets flagged, and the approved answer shows up in the Answer Library automatically. Killing and restarting a worker mid-run resumes rather than restarting from scratch.
