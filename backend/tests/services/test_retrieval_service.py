from unittest.mock import AsyncMock, patch

from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import DocumentStatus, KnowledgeDocument
from app.models.organization import Organization
from app.services.retrieval_service import retrieve_top_chunks


def _vector(dim_value_pairs, dim=768):
    v = [0.0] * dim
    for i, val in dim_value_pairs:
        v[i] = val
    return v


async def _create_org_and_document(db_session, name):
    org = Organization(name=name)
    db_session.add(org)
    await db_session.flush()
    document = KnowledgeDocument(
        org_id=org.id,
        title=f"{name} doc",
        source_file_key="k",
        source_file_ext="txt",
        status=DocumentStatus.indexed,
    )
    db_session.add(document)
    await db_session.flush()
    return org, document


@patch("app.services.retrieval_service.generate_embedding", new_callable=AsyncMock)
async def test_retrieve_top_chunks_orders_by_similarity_and_respects_top_k(mock_embed, db_session):
    mock_embed.return_value = _vector([(0, 1.0)])
    org, document = await _create_org_and_document(db_session, "Org A")

    close_chunk = KnowledgeChunk(
        document_id=document.id,
        org_id=org.id,
        text="close match",
        embedding=_vector([(0, 0.95), (1, 0.05)]),
    )
    far_chunk = KnowledgeChunk(
        document_id=document.id, org_id=org.id, text="far match", embedding=_vector([(1, 1.0)])
    )
    db_session.add_all([close_chunk, far_chunk])
    await db_session.commit()

    results = await retrieve_top_chunks(db_session, org.id, "irrelevant query text", top_k=1)

    assert len(results) == 1
    assert results[0].text == "close match"
    assert results[0].similarity > 0.9
    assert results[0].document_title == "Org A doc"


@patch("app.services.retrieval_service.generate_embedding", new_callable=AsyncMock)
async def test_retrieve_top_chunks_orders_all_results_when_under_top_k(mock_embed, db_session):
    mock_embed.return_value = _vector([(0, 1.0)])
    org, document = await _create_org_and_document(db_session, "Org B")

    db_session.add_all(
        [
            KnowledgeChunk(document_id=document.id, org_id=org.id, text="far", embedding=_vector([(2, 1.0)])),
            KnowledgeChunk(document_id=document.id, org_id=org.id, text="close", embedding=_vector([(0, 1.0)])),
        ]
    )
    await db_session.commit()

    results = await retrieve_top_chunks(db_session, org.id, "query", top_k=5)

    assert [r.text for r in results] == ["close", "far"]
    assert results[0].similarity > results[1].similarity


@patch("app.services.retrieval_service.generate_embedding", new_callable=AsyncMock)
async def test_retrieve_top_chunks_never_crosses_tenant_boundary(mock_embed, db_session):
    mock_embed.return_value = _vector([(0, 1.0)])
    org_a, doc_a = await _create_org_and_document(db_session, "Org A")
    org_b, doc_b = await _create_org_and_document(db_session, "Org B")

    # Org B's chunk is a PERFECT match for the query — if the org filter were broken (e.g.
    # applied after the fact, or missing), it would outrank org A's own much weaker match.
    db_session.add_all(
        [
            KnowledgeChunk(
                document_id=doc_a.id, org_id=org_a.id, text="org a weak match", embedding=_vector([(5, 1.0)])
            ),
            KnowledgeChunk(
                document_id=doc_b.id, org_id=org_b.id, text="org b perfect match", embedding=_vector([(0, 1.0)])
            ),
        ]
    )
    await db_session.commit()

    results = await retrieve_top_chunks(db_session, org_a.id, "query", top_k=5)

    assert len(results) == 1
    assert results[0].text == "org a weak match"


@patch("app.services.retrieval_service.generate_embedding", new_callable=AsyncMock)
async def test_retrieve_top_chunks_empty_knowledge_base(mock_embed, db_session):
    mock_embed.return_value = _vector([(0, 1.0)])
    org, _document = await _create_org_and_document(db_session, "Empty Org")

    results = await retrieve_top_chunks(db_session, org.id, "query", top_k=5)

    assert results == []
