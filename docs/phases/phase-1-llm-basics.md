# Phase 1 — LLM Basics (no RAG)

**Theme**: Upload questionnaire → parse → LLM drafts answers (no RAG yet) → export.
**Depends on**: Phase 0 (auth, orgs, tenant isolation).
**Read alongside this file**: `docs/architecture.md` §3 (backend), §6 (agent pipeline — only the Parser/Drafting shape, not the full graph yet), `docs/ui-ux.md` §6 (question workspace) and §2 (visual identity/design tokens — apply these, don't default to unstyled scaffolding).

This phase deliberately skips retrieval/citations — that's Phase 2. Confidence scores here can be a simple heuristic or LLM self-rating; don't over-build grounding logic that Phase 2 will replace.

## Sub-phases

### 1.1 File upload and storage
- Wire S3/MinIO (from Phase 0's Compose stack) for file storage.
- `RfpProject` entity: name, buyer, due date, owner, tags, source file.
- Upload endpoint + UI for a questionnaire file (XLSX, DOCX, PDF).
- **FR**: FR-RFP-01, FR-RFP-02.

### 1.2 Parser Agent v1
- Extract questions from XLSX (openpyxl) and DOCX (python-docx) first; PDF text extraction (non-scanned only — Textract/OCR is Phase 5).
- Detect sheets/columns, question vs. answer cells, sections, and a first pass at question type (yes/no, free text, multiple choice, numeric, attachment requested).
- `Question` entity: text, section, type, position (sheet/row/col).
- User-facing preview/correction step for detected questions and column mapping before drafting starts — this is a deliberate risk mitigation (client_requirements.md §16: "poor parsing" risk).
- **FR**: FR-RFP-03, FR-RFP-04.

### 1.3 Basic LLM drafting (no RAG)
- Straight prompt-based drafting: no retrieval, no citations yet. The prompt uses only the question text and org tone settings.
- `Answer` entity: text, choice (for structured question types), confidence (heuristic/self-rated), status.
- Org-level tone/style settings applied to every prompt (brand voice, length, forbidden phrases).
- Yes/no and multiple-choice questions return a structured choice plus optional comment.
- **FR**: FR-AI-06, FR-AI-08 (subset of FR-AI-01/02 — full versions land in Phase 2/4).
- **Quality rule that still applies even without RAG**: never invent specifics (cert numbers, dates, names) the model wasn't given — prefer a generic/hedged answer over a fabricated specific one.

### 1.4 Review UI
- Answer status lifecycle: `Not Started → AI Drafted → Needs Review → In Review → Approved / Rejected` (full lifecycle defined now even though auto-routing by confidence threshold comes in Phase 4).
- Manual edit/approve/reject in the question workspace.
- **FR**: FR-REV-01 (statuses only; FR-REV-02 auto-routing is Phase 4).

### 1.5 Export
- Export back into the original file format and layout (XLSX: fill answer cells, keep formatting; DOCX: fill answer sections).
- CSV export of questions/answers.
- Warning shown if any answers aren't yet approved at export time.
- **FR**: FR-EXP-01, FR-EXP-02 (partial — PDF export can wait), FR-EXP-04.

## Exit criteria — demo

Upload a real XLSX or DOCX questionnaire, see questions auto-detected and correctable, get AI drafts for every question (no citations yet), review/edit/approve them, and export a filled-in file in the original format.
