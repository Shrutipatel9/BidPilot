import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.embedding_provider import generate_embedding
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import KnowledgeDocument


@dataclass
class RetrievedChunk:
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_title: str
    page: int | None
    section: str | None
    text: str
    similarity: float


async def retrieve_top_chunks(
    db: AsyncSession, org_id: uuid.UUID, query_text: str, top_k: int = 5
) -> list[RetrievedChunk]:
    """Vector-only retrieval (hybrid search + re-ranking is Phase 3). Reused as-is by both
    grounded drafting (2.5) and the knowledge base search page (2.6) — only query_text/top_k
    differ per call site.

    The org_id filter is a plain column predicate directly in this query, not applied
    afterward — the "structurally enforced" shape docs/architecture.md §9 asks for on vector
    search specifically, since KnowledgeChunk.org_id is denormalized for exactly this."""
    query_vector = await generate_embedding(query_text)
    distance = KnowledgeChunk.embedding.cosine_distance(query_vector)

    result = await db.execute(
        select(KnowledgeChunk, KnowledgeDocument.title, distance.label("distance"))
        .join(KnowledgeDocument, KnowledgeDocument.id == KnowledgeChunk.document_id)
        .where(KnowledgeChunk.org_id == org_id)
        .order_by(distance)
        .limit(top_k)
    )

    return [
        RetrievedChunk(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            document_title=title,
            page=chunk.page,
            section=chunk.section,
            text=chunk.text,
            # pgvector's cosine_distance is 1 - cosine_similarity for normalized embeddings;
            # clamp defensively since floating-point error can push it fractionally outside
            # [0, 1].
            similarity=max(0.0, min(1.0, 1 - dist)),
        )
        for chunk, title, dist in result.all()
    ]
