import uuid
from unittest.mock import AsyncMock, patch

from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import DocumentStatus, KnowledgeDocument
from app.models.membership import Membership, MembershipRole


def _vector(dim_value_pairs, dim=768):
    v = [0.0] * dim
    for i, val in dim_value_pairs:
        v[i] = val
    return v


async def _signup(client, email, password="correct-horse-battery"):
    resp = await client.post("/api/auth/signup", json={"email": email, "password": password})
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


async def _create_org(client, token, name="Acme Inc"):
    resp = await client.post("/api/orgs", json={"name": name}, headers=_auth(token))
    return resp.json()["id"]


async def _add_member(client, db_session, org_id, email, role):
    token = await _signup(client, email)
    me = await client.get("/api/auth/me", headers=_auth(token))
    db_session.add(Membership(user_id=uuid.UUID(me.json()["id"]), org_id=uuid.UUID(org_id), role=role))
    await db_session.commit()
    return token


@patch("app.services.retrieval_service.generate_embedding", new_callable=AsyncMock)
async def test_search_returns_ranked_results_with_snippet(mock_embed, client, db_session):
    mock_embed.return_value = _vector([(0, 1.0)])

    token = await _signup(client, "owner1@example.com")
    org_id = await _create_org(client, token)

    document = KnowledgeDocument(
        org_id=uuid.UUID(org_id), title="Security Policy", source_file_key="k", source_file_ext="txt",
        status=DocumentStatus.indexed,
    )
    db_session.add(document)
    await db_session.flush()
    db_session.add(
        KnowledgeChunk(
            document_id=document.id, org_id=uuid.UUID(org_id), text="We encrypt all data at rest using AES-256.",
            page=None, section="Encryption", embedding=_vector([(0, 1.0)]),
        )
    )
    await db_session.commit()

    resp = await client.get(f"/api/orgs/{org_id}/knowledge/search?q=encryption", headers=_auth(token))
    assert resp.status_code == 200, resp.text
    results = resp.json()
    assert len(results) == 1
    assert results[0]["document_title"] == "Security Policy"
    assert results[0]["section"] == "Encryption"
    assert results[0]["snippet"].startswith("We encrypt all data at rest")
    assert results[0]["similarity"] > 0.9


@patch("app.services.retrieval_service.generate_embedding", new_callable=AsyncMock)
async def test_viewer_can_search(mock_embed, client, db_session):
    mock_embed.return_value = _vector([(0, 1.0)])
    owner_token = await _signup(client, "owner2@example.com")
    org_id = await _create_org(client, owner_token)
    viewer_token = await _add_member(client, db_session, org_id, "viewer2@example.com", MembershipRole.viewer)

    resp = await client.get(f"/api/orgs/{org_id}/knowledge/search?q=anything", headers=_auth(viewer_token))
    assert resp.status_code == 200


@patch("app.services.retrieval_service.generate_embedding", new_callable=AsyncMock)
async def test_search_tenant_isolation(mock_embed, client, db_session):
    mock_embed.return_value = _vector([(0, 1.0)])

    token_a = await _signup(client, "orga@example.com")
    org_a = await _create_org(client, token_a, "Org A")
    document = KnowledgeDocument(
        org_id=uuid.UUID(org_a), title="Org A Doc", source_file_key="k", source_file_ext="txt",
        status=DocumentStatus.indexed,
    )
    db_session.add(document)
    await db_session.flush()
    db_session.add(
        KnowledgeChunk(
            document_id=document.id, org_id=uuid.UUID(org_a), text="org a secret content",
            embedding=_vector([(0, 1.0)]),
        )
    )
    await db_session.commit()

    token_b = await _signup(client, "orgb@example.com")
    org_b = await _create_org(client, token_b, "Org B")

    resp = await client.get(f"/api/orgs/{org_a}/knowledge/search?q=secret", headers=_auth(token_b))
    assert resp.status_code == 403

    # Legitimate member of org B, using their own org_id, must see zero results — not org A's
    # content — even though it's a perfect match by similarity.
    resp = await client.get(f"/api/orgs/{org_b}/knowledge/search?q=secret", headers=_auth(token_b))
    assert resp.status_code == 200
    assert resp.json() == []
