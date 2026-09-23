# Phase 2 — RAG

**Theme**: Knowledge base upload, chunking, embeddings, pgvector, cited answers, confidence scores.
**Depends on**: Phase 1 (drafting pipeline exists; this phase grounds it).
**Read alongside this file**: `docs/architecture.md` §4 (data model: KnowledgeDocument/KnowledgeChunk), §6 (Retriever Agent).

## Sub-phases

### 2.1 Knowledge base upload and storage
- Upload knowledge sources: PDF, DOCX, XLSX, TXT, MD (Textract for scanned files is Phase 5 — plain-text-extractable files only for now).
- Tagging (Security, Legal, Product, HR, Infrastructure, ...) and expiry/review date.
- `KnowledgeDocument` entity.
- **FR**: FR-KB-01 (non-scanned subset), FR-KB-06.

### 2.2 Chunking
- Split documents by structure (headings, sections, tables), not fixed-size windows.
- **FR**: FR-KB-03.

### 2.3 Embeddings and pgvector
- Embed chunks (OpenAI or a local model for dev; Bedrock Titan swap comes in Phase 5) and store in Postgres+pgvector with metadata (source, page, section, owner, tags, date, version).
- `KnowledgeChunk` entity.
- Background ingestion via Celery/Redis with real-time progress in the UI.
- Document versioning: replacing a document re-indexes and removes old vectors.
- **FR**: FR-KB-04, FR-KB-07, FR-KB-09.

### 2.4 Retriever Agent v1 (vector-only)
- Given a question, run vector similarity search scoped to the org (`org_id` filter is mandatory — see `docs/architecture.md` §9).
- Hybrid search (+ keyword/BM25) and re-ranking are Phase 3 — this is vector-only.
- **FR**: FR-AI-03 (vector-only subset).

### 2.5 Drafting Agent with citations and confidence
- Extend Phase 1's drafting to use retrieved chunks as grounding context.
- Every factual claim must cite a source (document, page/section); no source → "Insufficient information" (never invent). This is the core AI quality rule from client_requirements.md §7.3 and is tested explicitly (`docs/testing.md`).
- Confidence score becomes retrieval-grounded (e.g. based on retrieval similarity + LLM self-assessment), replacing Phase 1's heuristic.
- **FR**: FR-AI-02, FR-AI-05.

### 2.6 Knowledge base search page
- Semantic + keyword search UI with source previews.
- **FR**: FR-KB-10 (keyword portion can be a simple ILIKE search until Phase 3's BM25 lands).

## Exit criteria — demo

Upload a policy document to the knowledge base, then draft answers for a questionnaire where at least some answers are grounded in that document with a visible citation and confidence score, and questions with no matching evidence come back as "Insufficient information" instead of a guess.
