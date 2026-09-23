# Phase 3 — Advanced RAG

**Theme**: Hybrid search, re-ranking, Answer Library, "Ask the Knowledge Base" chat, eval suite.
**Depends on**: Phase 2 (vector RAG pipeline exists).
**Read alongside this file**: `docs/architecture.md` §6 (Retriever Agent detail), `docs/testing.md` §5 (AI evaluation).

## Sub-phases

### 3.1 Hybrid search
- Add keyword/BM25 search alongside vector search in the Retriever Agent.
- **FR**: FR-AI-03 (completes it).

### 3.2 Re-ranking
- Second-pass re-ranking of combined hybrid results before they reach the Drafting Agent.
- **FR**: FR-AI-03 (completes it).

### 3.3 Answer Library
- `LibraryAnswer` entity: question, answer, embedding, tags, `is_gold`, approved_by, source_project.
- Import past completed questionnaires as Q&A pairs.
- Knowledge Managers can approve/edit/retire/mark-gold library answers.
- Retriever/Drafting prefer library answers over raw documents when they match closely.
- One-click promotion of an approved answer into the library (also used by Phase 4's Learning node, but the library and promotion UI are built here first).
- **FR**: FR-KB-05, FR-KB-11, FR-AI-04, FR-REV-05.

### 3.4 Duplicate question detection
- Detect duplicate/near-duplicate questions within a questionnaire (embedding similarity) and answer once.
- **FR**: FR-RFP-09.

### 3.5 "Ask the Knowledge Base" chat
- Free-form Q&A over the knowledge base with cited answers, reusing the hybrid retrieval + drafting stack.
- **FR**: FR-AI-14.

### 3.6 Eval suite v1
- Golden dataset + RAGAS or custom LLM-as-judge scoring: faithfulness, answer relevance, context precision, citation accuracy.
- Not run on every commit (cost) — see `docs/testing.md` for when it runs.
- **NFR**: NFR-09.

## Exit criteria — demo

Retrieval visibly improves (better top-k relevance) after adding hybrid search + re-ranking vs. Phase 2's vector-only baseline; a question matching a prior approved answer pulls it from the Answer Library instead of re-deriving from raw documents; "Ask the KB" answers a free-form question with citations; the eval suite produces a faithfulness/citation-accuracy report on the golden dataset.
