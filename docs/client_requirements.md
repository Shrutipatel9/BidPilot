# BidPilot: AI Copilot for RFPs and Security Questionnaires

**Document:** Client Requirements (Source of Truth)
**Version:** 1.0
**Date:** 23 September 2026
**Status:** Baseline, approved for planning

> This document describes the whole project: what we are building, who it is for, and what it must do. It is the single source of truth. Detailed specs, designs and code must trace back to requirement IDs in this file (for example `FR-DOC-01`). Any change to scope must update this file first.

---

## 1. Project Summary

BidPilot is a multi-tenant SaaS platform, built around AI agents, that helps B2B companies answer **RFPs (Requests for Proposal), RFIs, and security or compliance questionnaires** (for example CAIQ, SIG, vendor assessments and custom Excel questionnaires) quickly and accurately.

A user uploads a questionnaire in Excel, Word or PDF format. BidPilot parses it, understands each question, finds the best evidence in the company's knowledge base, drafts an answer with citations and a confidence score, routes low-confidence answers to human experts for review, and exports the finished response **in the original file format**.

Unlike a basic "chat with your PDF" app, BidPilot runs a **multi-agent workflow (LangGraph)** with human review steps, evaluation, cost tracking and billing, the way an AI product works in production.

---

## 2. Business Problem

| Problem | Impact today |
|---|---|
| RFPs and security questionnaires contain 100–500 questions each | 2–10 working days per response |
| Most questions have been answered before, in past bids | Teams copy and paste from old files, with inconsistent results |
| Answers are spread across Drive, wikis, policy PDFs and people's heads | Subject-matter experts (SMEs) get interrupted repeatedly |
| Outdated or wrong answers get submitted | Compliance risk and lost deals |
| No visibility into bid progress | Deadlines slip |

**Goal:** cut the time to respond by **70% or more**, with answers that are accurate, cite their sources and have been approved by a person.

---

## 3. Objectives

### 3.1 Business objectives
1. Produce a first draft of a 200-question questionnaire in **under 10 minutes**.
2. Automatically answer **60% or more** of questions with high confidence.
3. Build a reusable, continuously improving **company knowledge base** of approved answers.
4. Earn revenue through subscription plans and usage-based credits (Stripe).

### 3.2 Learning and technical objectives (internal)
The project is also a hands-on way to learn production GenAI engineering. It must meaningfully cover:
- Prompt engineering
- Embeddings and vector databases
- RAG (basic to advanced: hybrid search, re-ranking, citations)
- LangChain and LangGraph
- AI agents with tools, multi-agent orchestration and human review steps
- AI workflows (stateful, resumable, run in parallel)
- AWS AI services (Bedrock, Bedrock Knowledge Bases, Guardrails, Textract, Comprehend, S3)
- LLM evaluation, observability and cost control
- Production concerns: Redis, Docker, payments, security, multi-tenancy

---

## 4. Target Users and Roles

### 4.1 Target customers
- B2B SaaS and IT services companies
- Agencies and consulting firms that bid for projects
- Security, compliance and presales teams

### 4.2 User roles (per organization)

| Role | Description | Key permissions |
|---|---|---|
| **Owner** | Created the organization | Everything, including billing and deleting the organization |
| **Admin** | Manages the workspace | Users, roles, settings, knowledge base, all projects |
| **Knowledge Manager** | Curates the knowledge base | Upload and approve knowledge sources, manage the answer library |
| **Responder** | Works on bids | Create RFP projects, run AI drafting, edit answers |
| **Reviewer (SME)** | Subject-matter expert | Review, approve or reject assigned answers |
| **Viewer** | Read-only | View projects and exports |

### 4.3 Platform role
| Role | Description |
|---|---|
| **Super Admin** | Internal operator. Manages tenants, plans, usage, abuse, system health |

---

## 5. Scope

### 5.1 In scope
- Multi-tenant web application (React frontend, Python FastAPI backend)
- Knowledge base management (upload, parse, embed, version)
- Questionnaire upload and parsing (XLSX, DOCX, PDF including scanned files)
- AI answer generation through a multi-agent workflow
- Human review and approval workflow
- Export in the original format
- Reusable answer library that learns from approved answers
- Billing with Stripe (subscriptions and credits)
- Admin, usage and analytics dashboards
- Evaluation, observability and cost tracking of AI features
- Tender Discovery Agent (Phase 7, optional)

### 5.2 Out of scope (v1)
- Native mobile apps
- Real-time co-editing of the same answer by several people at once (Google Docs style)
- Submitting responses directly to buyer portals
- Fine-tuning or training custom LLMs
- On-premise deployment
- Languages other than English (the design should allow them later)

---

## 6. Functional Requirements

### 6.1 Authentication and organization management (`FR-AUTH`)
| ID | Requirement |
|---|---|
| FR-AUTH-01 | Users can sign up and log in with email and password (JWT access tokens plus refresh tokens) |
| FR-AUTH-02 | Google OAuth login |
| FR-AUTH-03 | Email verification and password reset |
| FR-AUTH-04 | A user can create an organization and invite members by email with a role |
| FR-AUTH-05 | Role-based access control enforced in both the API and the UI |
| FR-AUTH-06 | All data is strictly separated by organization; one tenant can never see another tenant's data |
| FR-AUTH-07 | Audit log of important actions (logins, approvals, exports, deletions, role changes) |

### 6.2 Knowledge base (`FR-KB`)
| ID | Requirement |
|---|---|
| FR-KB-01 | Upload knowledge sources: PDF, DOCX, XLSX, TXT, MD, and past completed RFPs or questionnaires |
| FR-KB-02 | Scanned PDFs and images are converted to text with **AWS Textract**, keeping tables |
| FR-KB-03 | Documents are split into chunks by structure (headings, sections, tables), not only by fixed size |
| FR-KB-04 | Chunks are embedded and stored in the vector database, with metadata: source, page, section, owner, tags, date, version |
| FR-KB-05 | Past completed questionnaires are imported as **question and answer pairs** into the Answer Library |
| FR-KB-06 | Documents can be tagged (for example Security, Legal, Product, HR, Infrastructure) and given an expiry or review date |
| FR-KB-07 | Documents have versions; replacing a document re-indexes it and removes the old vectors |
| FR-KB-08 | Personal data (PII) in documents is detected with **AWS Comprehend** and can be redacted before indexing |
| FR-KB-09 | Ingestion runs in the background (Redis and Celery) and shows progress in real time |
| FR-KB-10 | Knowledge base search page: semantic and keyword search with previews of the source |
| FR-KB-11 | Knowledge Managers can approve, edit, retire or mark answers in the Answer Library as "gold" (preferred) |

### 6.3 RFP and questionnaire projects (`FR-RFP`)
| ID | Requirement |
|---|---|
| FR-RFP-01 | Create a project with name, client or buyer name, due date, owner and tags |
| FR-RFP-02 | Upload a questionnaire file (XLSX, DOCX, PDF) |
| FR-RFP-03 | The system detects questions automatically: sheets, columns, question and answer cells, sections, and question types (yes/no, free text, multiple choice, numeric, attachment requested) |
| FR-RFP-04 | The user can preview and correct detected questions and map columns before drafting starts |
| FR-RFP-05 | Each question is classified by category (Security, Privacy, Legal, Product, Commercial and so on) and by difficulty |
| FR-RFP-06 | Project dashboard: progress (drafted, in review, approved), counts by confidence level, deadline countdown |
| FR-RFP-07 | Questions can be assigned to reviewers, individually or in bulk by category |
| FR-RFP-08 | Comments and mentions (@user) on each question |
| FR-RFP-09 | Duplicate or near-duplicate questions in a questionnaire are detected and answered once |

### 6.4 AI drafting: multi-agent workflow (`FR-AI`)
| ID | Requirement |
|---|---|
| FR-AI-01 | Drafting runs as a **LangGraph** stateful workflow (see Section 7) |
| FR-AI-02 | Each answer includes: draft text, **citations** (source document, page or section), a **confidence score** (0–100) and a short explanation of the reasoning |
| FR-AI-03 | Retrieval uses **hybrid search** (vector plus keyword/BM25) followed by **re-ranking** |
| FR-AI-04 | Approved answers in the Answer Library are preferred over raw documents when they match closely |
| FR-AI-05 | If evidence is insufficient, the AI must say **"Insufficient information"** and flag the question for a person. It must never invent an answer |
| FR-AI-06 | Yes/no and multiple-choice questions return a structured choice plus an optional comment |
| FR-AI-07 | Users can re-generate one answer with instructions (for example "shorter", "more formal", "mention ISO 27001") |
| FR-AI-08 | Organization-level settings for tone and style (brand voice, answer length, forbidden phrases) are applied to every prompt |
| FR-AI-09 | Questions are drafted in parallel batches, and progress streams to the UI in real time (WebSocket or SSE) |
| FR-AI-10 | Workflow state is checkpointed so it can resume after a failure or after a human review pause |
| FR-AI-11 | The LLM provider can be switched per environment: **AWS Bedrock** (Claude, Llama), OpenAI, or a local model |
| FR-AI-12 | **Bedrock Guardrails** (or an equivalent layer) filter unsafe output, and prompt injection from uploaded documents is blocked |
| FR-AI-13 | A **Compliance Checker Agent** checks that drafts agree with policy documents and with each other (for example, the same encryption answer everywhere) |
| FR-AI-14 | "Ask the Knowledge Base" chat: users can ask free-form questions about the knowledge base and get cited answers |

### 6.5 Review and approval (`FR-REV`)
| ID | Requirement |
|---|---|
| FR-REV-01 | Answer statuses: `Not Started → AI Drafted → Needs Review → In Review → Approved / Rejected` |
| FR-REV-02 | Answers below a set confidence threshold go to review automatically |
| FR-REV-03 | Reviewers can edit, approve or reject an answer with a comment; rejected answers can be re-drafted by the AI using the feedback |
| FR-REV-04 | Full edit history for each answer (AI draft compared with human edits) |
| FR-REV-05 | Approved answers can be **promoted to the Answer Library** with one click, so the system keeps improving |
| FR-REV-06 | Notifications (in-app and email) for assignments, mentions, approaching due dates and completed drafting |

### 6.6 Export (`FR-EXP`)
| ID | Requirement |
|---|---|
| FR-EXP-01 | Export back into the **original file format and layout** (XLSX: fill the answer cells and keep formatting; DOCX: fill the answer sections) |
| FR-EXP-02 | Additional exports: clean PDF or DOCX response document, and a CSV of questions and answers |
| FR-EXP-03 | Optional export of an internal citations report for auditors |
| FR-EXP-04 | A warning is shown if any answers are not yet approved at export time |

### 6.7 Tender Discovery Agent, Phase 7, optional (`FR-TND`)
| ID | Requirement |
|---|---|
| FR-TND-01 | The organization defines a profile: services, industries, locations, contract size range, certifications |
| FR-TND-02 | A tool-using agent searches permitted sources (public APIs, RSS feeds, allowed web search) for matching tenders or RFPs |
| FR-TND-03 | Each match gets a fit score, a summary, eligibility criteria, deadline and required documents |
| FR-TND-04 | One click turns a discovered tender into an RFP project |
| FR-TND-05 | Scheduled daily digest by email or in-app |
| FR-TND-06 | Only sources whose terms permit automated access are used |

### 6.8 Billing and subscriptions (`FR-BILL`)
| ID | Requirement |
|---|---|
| FR-BILL-01 | Stripe Checkout for subscriptions; Stripe Customer Portal for plan changes, invoices and payment methods |
| FR-BILL-02 | Plans have usage limits (see Section 9); usage is tracked in credits (1 question drafted = 1 credit) |
| FR-BILL-03 | One-time credit top-up packs |
| FR-BILL-04 | Stripe webhooks keep subscription status in sync (created, updated, cancelled, payment failed); webhook handling is idempotent (safe to receive twice) |
| FR-BILL-05 | 14-day free trial with a limited number of credits |
| FR-BILL-06 | Clear feedback when a limit is reached: soft warning at 80%, hard block at 100% with an upgrade button |

### 6.9 Dashboards and analytics (`FR-ANL`)
| ID | Requirement |
|---|---|
| FR-ANL-01 | Organization dashboard: active projects, upcoming deadlines, automation rate, time saved, credits used |
| FR-ANL-02 | AI quality metrics: average confidence, approval rate without edits, most-edited categories |
| FR-ANL-03 | Knowledge base health: stale documents, questions with no good source (gaps to fill) |
| FR-ANL-04 | Super Admin dashboard: tenants, revenue, LLM token cost per tenant, error rates |

---

## 7. AI Agent Architecture (LangGraph)

### 7.1 Agents and responsibilities

| # | Agent / node | Responsibility | Tools / services |
|---|---|---|---|
| 1 | **Parser Agent** | Extract questions and structure from the uploaded file | openpyxl, python-docx, PDF parser, **AWS Textract** |
| 2 | **Classifier Agent** | Categorize each question and detect its type; remove duplicates | LLM (structured output), embeddings |
| 3 | **Retriever Agent** | Plan search queries, run hybrid search, re-rank, check the Answer Library first | Vector DB, keyword search, re-ranker |
| 4 | **Drafting Agent** | Write the answer with citations and a confidence score in the organization's tone | LLM (Bedrock or OpenAI), prompt templates |
| 5 | **Compliance Checker Agent** | Check consistency with policies and other answers; flag contradictions | LLM-as-judge, retrieval |
| 6 | **Router / Supervisor** | Decide: auto-approve suggestion, send to a person for review, or retry | Rules plus LLM |
| 7 | **Human Review node** | Pause the workflow until a reviewer acts, then resume | LangGraph interrupt and checkpointer |
| 8 | **Learning node** | Save approved answers to the Answer Library with embeddings | Vector DB |
| 9 | **Tender Scout Agent** (Phase 7) | Discover external opportunities | Web search and API tools |

### 7.2 Workflow (high level)

```
Upload file
   │
   ▼
[Parser Agent] ──► user confirms column/question mapping
   │
   ▼
[Classifier Agent] ──► remove duplicates, add categories
   │
   ▼  (parallel batches per question)
[Retriever Agent] ──► [Drafting Agent] ──► [Compliance Checker]
                                               │
                                               ▼
                                      [Router / Supervisor]
                         ┌──────────────┼────────────────┐
                  high confidence   low confidence   failed or contradiction
                         │              │                │
                  "AI Drafted"   [Human Review]   retry, max 2 times
                         │              │  (interrupt)
                         └──────► Approved ◄───┘
                                      │
                                      ▼
                              [Learning node] ──► Answer Library
                                      │
                                      ▼
                                   Export
```

### 7.3 AI quality rules
- Every factual claim in an answer must be supported by a retrieved source. If there is no source, the answer is marked "Insufficient information".
- Prompts are versioned and stored centrally. Changes are evaluated against a test set before release.
- Text from uploaded documents is treated as **data, never instructions** (defense against prompt injection).
- Personal data is detected and masked before it is sent to external LLMs, where the organization has enabled this.

---

## 8. Non-Functional Requirements (`NFR`)

| ID | Category | Requirement |
|---|---|---|
| NFR-01 | Performance | A 200-question questionnaire is drafted in under 10 minutes; knowledge base search answers in under 2 seconds (p95) |
| NFR-02 | Scalability | Background workers scale horizontally; the system supports 100+ tenants and 1M+ vector chunks |
| NFR-03 | Availability | Target 99.5% uptime; jobs are resumable after crashes |
| NFR-04 | Security | HTTPS everywhere; encryption at rest (database and S3); secrets in environment variables or AWS Secrets Manager; OWASP Top 10 protections |
| NFR-05 | Tenant isolation | Every query is filtered by `org_id`; vector searches always filter by tenant; tests enforce this |
| NFR-06 | Privacy | Customer data is never used to train models; organizations can delete all their data |
| NFR-07 | Rate limiting | Per-user and per-organization API rate limits using Redis |
| NFR-08 | Observability | Structured logs, error tracking, **LLM tracing (Langfuse or LangSmith)**, token and cost tracking per request |
| NFR-09 | AI evaluation | Automated eval suite (RAGAS or LLM-as-judge) covering faithfulness, answer relevance, context precision and citation accuracy |
| NFR-10 | Cost control | Token budget per organization; responses cached in Redis for identical questions; cheaper models for classification |
| NFR-11 | Maintainability | Clean modular code, type hints, linting, 70% or more test coverage on core services |
| NFR-12 | Deployability | Fully containerized with Docker; one-command local setup with `docker compose up` |
| NFR-13 | Accessibility | UI meets WCAG 2.1 AA basics (keyboard navigation, contrast, labels) |

---

## 9. Plans and Pricing (indicative)

| Plan | Price (per month) | Credits per month | Users | Features |
|---|---|---|---|---|
| **Trial** | Free, 14 days | 100 | 2 | Core drafting, 1 project |
| **Starter** | $49 | 1,000 | 3 | Knowledge base up to 200 documents, XLSX/DOCX export |
| **Pro** | $149 | 5,000 | 10 | Compliance checker, analytics, Answer Library, priority queue |
| **Business** | $399 | 20,000 | Unlimited | SSO (later), audit exports, Tender Discovery, custom tone |
| **Top-up pack** | $20 | +500 | – | One-time purchase |

*Prices are placeholders for Stripe test mode and can change.*

---

## 10. Technology Stack

| Layer | Technology |
|---|---|
| **Frontend** | React (Vite), JavaScript, React Router, TanStack Query, Tailwind CSS, WebSocket/SSE client |
| **Backend API** | Python, FastAPI, Pydantic, SQLAlchemy, Alembic |
| **AI orchestration** | LangChain, **LangGraph** (agents, state, checkpoints, human review steps) |
| **LLMs** | **AWS Bedrock** (Claude, Llama, Titan), OpenAI (optional), a local model through Ollama (optional, for development) |
| **Embeddings** | Bedrock Titan Embeddings / OpenAI embeddings (configurable) |
| **Vector DB** | **PostgreSQL + pgvector** (primary); Amazon OpenSearch Serverless or Qdrant (for comparison) |
| **Managed RAG (comparison)** | **AWS Bedrock Knowledge Bases** |
| **Relational DB** | PostgreSQL |
| **Cache / queue** | **Redis** (cache, rate limits, Celery broker, pub/sub for progress events) |
| **Background jobs** | Celery workers (ingestion, drafting, exports, scheduled jobs) |
| **Document AI** | **AWS Textract** (OCR and tables), openpyxl, python-docx, PDF parsing libraries |
| **Privacy / safety** | **AWS Comprehend** (PII detection), **Bedrock Guardrails** |
| **File storage** | **AWS S3** (MinIO for local development) |
| **Payments** | **Stripe** (Checkout, Customer Portal, Webhooks) |
| **Observability** | Langfuse or LangSmith (LLM tracing), Sentry, structured logging |
| **Evaluation** | RAGAS / custom LLM-as-judge suite |
| **DevOps** | **Docker**, Docker Compose, GitHub Actions CI; deploy target: AWS (ECS or EC2) |

---

## 11. High-Level Architecture

```
            ┌────────────────────────────┐
            │     React Web App (SPA)    │
            └─────────────┬──────────────┘
                          │ REST + WebSocket/SSE
            ┌─────────────▼──────────────┐
            │      FastAPI Backend       │── Stripe (Checkout, Webhooks)
            │ Auth · RBAC · Projects ·   │
            │ KB · Billing · Exports     │
            └──┬──────────┬──────────┬───┘
               │          │          │
        ┌──────▼───┐ ┌────▼────┐ ┌───▼─────────────┐
        │PostgreSQL│ │  Redis  │ │ S3 (files)      │
        │+ pgvector│ │cache/q  │ └─────────────────┘
        └──────▲───┘ └────┬────┘
               │          │ tasks
        ┌──────┴──────────▼────────────────────────┐
        │   Celery Workers + LangGraph Agents       │
        │ Parser · Classifier · Retriever · Drafter │
        │ Compliance · Router · Learning · Scout    │
        └──────┬───────────────────────────────────┘
               │
   ┌───────────▼──────────────────────────────────────┐
   │ AWS AI: Bedrock (LLM/Embeddings/Guardrails/KB),  │
   │ Textract, Comprehend  ·  Langfuse/LangSmith      │
   └──────────────────────────────────────────────────┘
```

---

## 12. Core Data Entities (high level)

| Entity | Key fields |
|---|---|
| Organization | id, name, plan, stripe_customer_id, settings (tone, thresholds) |
| User | id, email, name, auth provider |
| Membership | user_id, org_id, role |
| KnowledgeDocument | id, org_id, title, s3_key, type, tags, version, status, review_date |
| KnowledgeChunk | id, document_id, org_id, text, embedding, metadata (page, section) |
| LibraryAnswer | id, org_id, question, answer, embedding, tags, is_gold, approved_by, source_project |
| RfpProject | id, org_id, name, buyer, due_date, status, owner_id, source_file |
| Question | id, project_id, text, section, type, category, position (sheet/row/col), duplicate_of |
| Answer | id, question_id, text, choice, confidence, citations, status, assignee, version |
| AnswerRevision | id, answer_id, text, author (AI/user), created_at |
| Comment | id, question_id, user_id, body |
| WorkflowRun | id, project_id, graph_state_ref, status, tokens_used, cost |
| UsageLedger | id, org_id, credits_delta, reason, created_at |
| Subscription | id, org_id, stripe_subscription_id, plan, status, period_end |
| AuditLog | id, org_id, actor, action, entity, timestamp |
| TenderLead (Phase 7) | id, org_id, source, title, summary, fit_score, deadline, url |

---

## 13. Delivery Phases (learning-driven roadmap)

| Phase | Theme | Main deliverables | Concepts learned |
|---|---|---|---|
| **0** | Foundation | Monorepo, Docker Compose (API, web, Postgres, Redis, MinIO), authentication, organizations, role-based access | Production project setup |
| **1** | LLM basics | Upload questionnaire → parse → LLM drafts answers (no RAG) → export | **Prompt engineering**, structured output |
| **2** | RAG | Knowledge base upload, chunking, embeddings, pgvector, cited answers, confidence scores | **Embeddings, vector DB, RAG** |
| **3** | Advanced RAG | Hybrid search, re-ranking, Answer Library, "Ask the Knowledge Base" chat, eval suite | **LangChain**, RAG evaluation |
| **4** | Agents and workflows | LangGraph multi-agent pipeline, compliance checker, human review, checkpoints, running in parallel, real-time progress | **LangGraph, AI agents, AI workflows** |
| **5** | AWS AI | Bedrock models and embeddings, Textract, Comprehend PII, Guardrails, compare with Bedrock Knowledge Bases | **AWS AI services** |
| **6** | Production and SaaS | Stripe billing and credits, Redis rate limits and caching, analytics, observability, cost tracking, CI/CD, AWS deploy | Production engineering |
| **7** | Bonus | Tender Discovery Agent with scheduled digests | Tool-using autonomous agents |

Each phase must end with a **working, demo-able product increment**.

---

## 14. Success Metrics (acceptance-level)

| Metric | Target |
|---|---|
| Draft time for 200 questions | Under 10 minutes |
| Answers approved without edits | 60% or more (on the test dataset) |
| Faithfulness score (eval) | 0.85 or higher |
| Citation accuracy (citation actually supports the answer) | 90% or higher |
| Hallucination on questions with no available answer | The AI returns "Insufficient information" 95% or more of the time |
| Export fidelity | 100% of answers land in the correct cells or sections |
| Cross-tenant data leakage | Zero (checked by automated tests) |

---

## 15. Assumptions

1. Public sample questionnaires (for example the CSA CAIQ and public RFP templates) plus synthetic company documents will be used as test data.
2. An AWS account with Bedrock model access is available; OpenAI or a local model is the fallback.
3. Stripe runs in **test mode** until launch.
4. English only in v1.
5. The single-region deployment on AWS is acceptable for v1.

---

## 16. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| LLM hallucination | Strict grounding, "insufficient information" fallback, compliance checker, human review, evals |
| Poor parsing of complex Excel or PDF layouts | User-confirmed column mapping step, Textract fallback, test suite of real formats |
| LLM cost overruns | Credits, per-org budgets, caching, smaller models for simple steps, cost dashboard |
| Prompt injection through uploaded docs | Treat document text as data, Guardrails, output validation |
| Data leakage between tenants | Mandatory org filters, row-level checks, isolation tests |
| Vendor lock-in | LLM, embedding and vector store providers can be swapped through configuration |

---

## 17. Glossary

| Term | Meaning |
|---|---|
| **RFP / RFI** | Request for Proposal / Request for Information: a buyer's document asking vendors to respond |
| **Security questionnaire** | A vendor risk assessment (for example CAIQ, SIG) asking about security and compliance practices |
| **RAG** | Retrieval-Augmented Generation: the LLM answers using retrieved documents |
| **Embedding** | A numeric vector that represents the meaning of text |
| **Hybrid search** | Combining semantic (vector) search with keyword search |
| **Re-ranking** | A second pass that reorders retrieved results by relevance |
| **LangGraph** | A framework for building stateful, multi-step, multi-agent LLM workflows |
| **Human review step (human-in-the-loop)** | A workflow step that pauses until a person reviews or approves |
| **Answer Library** | A curated set of approved question and answer pairs that are reused first |
| **Credit** | A billing unit; 1 credit is used per question drafted |

---

## 18. Change Log

| Version | Date | Change |
|---|---|---|
| 1.0 | 23 Sep 2026 | Initial baseline |
