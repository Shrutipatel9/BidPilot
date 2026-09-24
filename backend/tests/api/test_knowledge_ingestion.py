import io
import uuid
from unittest.mock import AsyncMock, patch

from sqlalchemy import select

from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import DocumentStatus, KnowledgeDocument
from app.services.ingestion_service import ingest_document


async def _signup(client, email, password="correct-horse-battery"):
    resp = await client.post("/api/auth/signup", json={"email": email, "password": password})
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


async def _create_org(client, token, name="Acme Inc"):
    resp = await client.post("/api/orgs", json={"name": name}, headers=_auth(token))
    return resp.json()["id"]


async def _create_document(client, org_id, token, filename, content, content_type="text/plain"):
    resp = await client.post(
        f"/api/orgs/{org_id}/knowledge/documents",
        files={"file": (filename, io.BytesIO(content), content_type)},
        data={"title": filename},
        headers=_auth(token),
    )
    return resp.json()["id"]


@patch("app.services.ingestion_service.generate_embedding", new_callable=AsyncMock)
async def test_ingest_txt_document_creates_chunks(mock_embed, client, db_session):
    mock_embed.return_value = [0.1] * 768

    token = await _signup(client, "owner1@example.com")
    org_id = await _create_org(client, token)
    content = b"# Security\n\nWe encrypt data at rest.\n\n# Access Control\n\nMFA is required."
    document_id = await _create_document(client, org_id, token, "policy.md", content, "text/markdown")

    await ingest_document(uuid.UUID(document_id))

    document = await db_session.get(KnowledgeDocument, uuid.UUID(document_id))
    assert document.status == DocumentStatus.indexed

    chunks = (
        await db_session.execute(select(KnowledgeChunk).where(KnowledgeChunk.document_id == uuid.UUID(document_id)))
    ).scalars().all()
    assert len(chunks) == 2
    sections = {c.section for c in chunks}
    assert sections == {"Security", "Access Control"}
    assert all(len(c.embedding) == 768 for c in chunks)
    assert all(c.org_id == uuid.UUID(org_id) for c in chunks)


@patch("app.services.ingestion_service.generate_embedding", new_callable=AsyncMock)
async def test_replace_document_removes_old_chunks(mock_embed, client, db_session):
    mock_embed.return_value = [0.2] * 768

    token = await _signup(client, "owner2@example.com")
    org_id = await _create_org(client, token)
    document_id = await _create_document(client, org_id, token, "v1.txt", b"Original content paragraph.")
    await ingest_document(uuid.UUID(document_id))

    chunks_before = (
        await db_session.execute(select(KnowledgeChunk).where(KnowledgeChunk.document_id == uuid.UUID(document_id)))
    ).scalars().all()
    assert len(chunks_before) == 1

    resp = await client.post(
        f"/api/orgs/{org_id}/knowledge/documents/{document_id}/replace",
        files={"file": ("v2.txt", io.BytesIO(b"Completely different replacement content."), "text/plain")},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["version"] == 2

    # replace_document already deletes old chunks synchronously (before re-ingestion runs).
    chunks_after_replace = (
        await db_session.execute(select(KnowledgeChunk).where(KnowledgeChunk.document_id == uuid.UUID(document_id)))
    ).scalars().all()
    assert len(chunks_after_replace) == 0

    await ingest_document(uuid.UUID(document_id))
    chunks_after_reingest = (
        await db_session.execute(select(KnowledgeChunk).where(KnowledgeChunk.document_id == uuid.UUID(document_id)))
    ).scalars().all()
    assert len(chunks_after_reingest) == 1
    assert chunks_after_reingest[0].text != chunks_before[0].text


async def test_ingest_missing_document_is_a_noop(client, db_session):
    # `client` isn't used directly, but its fixture is what patches async_session_factory to
    # the test's own transaction — without it this would hit the real dev database instead.
    # Doesn't raise — just logs and returns, matching drafting_service's same-shaped guard.
    await ingest_document(uuid.uuid4())


@patch("app.services.ingestion_service.generate_embedding", new_callable=AsyncMock)
async def test_all_chunks_failing_to_embed_marks_document_failed(mock_embed, client, db_session):
    from app.core.embedding_provider import EmbeddingError

    mock_embed.side_effect = EmbeddingError("provider down")

    token = await _signup(client, "owner3@example.com")
    org_id = await _create_org(client, token)
    document_id = await _create_document(client, org_id, token, "policy.txt", b"Some content here.")

    await ingest_document(uuid.UUID(document_id))

    document = await db_session.get(KnowledgeDocument, uuid.UUID(document_id))
    assert document.status == DocumentStatus.failed

    chunks = (
        await db_session.execute(select(KnowledgeChunk).where(KnowledgeChunk.document_id == uuid.UUID(document_id)))
    ).scalars().all()
    assert len(chunks) == 0
