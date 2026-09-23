# Phase 5 — AWS AI

**Theme**: Bedrock models and embeddings, Textract, Comprehend PII, Guardrails, compare with Bedrock Knowledge Bases.
**Depends on**: Phase 4 (full agent pipeline exists and is provider-agnostic by design — this phase plugs AWS in behind that abstraction, it doesn't rebuild the pipeline).
**Read alongside this file**: `docs/architecture.md` §3/§6 (wherever the LLM/embedding provider interface is defined).

## Sub-phases

### 5.1 Bedrock LLM and embeddings
- Add Bedrock (Claude, Llama, Titan) as a selectable provider alongside OpenAI/local, switchable per environment via config — not a hardcoded swap.
- **FR**: FR-AI-11.

### 5.2 Textract for scanned documents
- OCR + table extraction for scanned PDFs and images, both in knowledge base ingestion (Phase 2) and questionnaire parsing (Phase 1).
- **FR**: FR-KB-02 (completes it), extends FR-RFP-03 to scanned inputs.

### 5.3 Comprehend PII detection
- Detect PII in uploaded documents; optionally redact before indexing.
- **FR**: FR-KB-08.

### 5.4 Bedrock Guardrails and prompt-injection defense
- Guardrails (or equivalent) filter unsafe output; uploaded document text is enforced as data-never-instructions at the prompt-construction layer (defense in depth with whatever was already done ad hoc in Phase 1-4).
- **FR**: FR-AI-12.

### 5.5 Bedrock Knowledge Bases comparison (learning spike)
- Stand up Bedrock KB against the same corpus used by the pgvector pipeline and compare retrieval quality/cost using the Phase 3 eval suite. This is explicitly a comparison exercise (client_requirements.md §10, §13) — it does not need to replace the primary pgvector pipeline unless the comparison motivates that.

## Exit criteria — demo

Same questionnaire-drafting demo as Phase 4, but running against Bedrock instead of the dev-time provider with no pipeline code changes beyond config; a scanned PDF questionnaire and a scanned PDF knowledge document both parse correctly via Textract; a document containing PII gets flagged/redacted; an attempted prompt-injection string inside an uploaded document is neutralized (logged, not obeyed).
