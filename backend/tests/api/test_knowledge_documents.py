import io
import uuid

from app.models.membership import Membership, MembershipRole


async def _signup(client, email, password="correct-horse-battery"):
    resp = await client.post("/api/auth/signup", json={"email": email, "password": password})
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


async def _create_org(client, token, name="Acme Inc"):
    resp = await client.post("/api/orgs", json={"name": name}, headers=_auth(token))
    return resp.json()["id"]


def _fake_txt_file():
    return {"file": ("policy.txt", io.BytesIO(b"We encrypt all data at rest using AES-256."), "text/plain")}


async def _add_member(client, db_session, org_id, email, role):
    token = await _signup(client, email)
    me = await client.get("/api/auth/me", headers=_auth(token))
    db_session.add(Membership(user_id=uuid.UUID(me.json()["id"]), org_id=uuid.UUID(org_id), role=role))
    await db_session.commit()
    return token


async def test_create_list_get_document(client):
    token = await _signup(client, "owner1@example.com")
    org_id = await _create_org(client, token)

    resp = await client.post(
        f"/api/orgs/{org_id}/knowledge/documents",
        files=_fake_txt_file(),
        data={"title": "Security Policy", "tags": '["Security"]'},
        headers=_auth(token),
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["title"] == "Security Policy"
    assert body["tags"] == ["Security"]
    assert body["status"] == "uploaded"
    assert body["source_file_ext"] == "txt"
    assert body["version"] == 1

    resp = await client.get(f"/api/orgs/{org_id}/knowledge/documents", headers=_auth(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = await client.get(f"/api/orgs/{org_id}/knowledge/documents/{body['id']}", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["id"] == body["id"]


async def test_reject_unsupported_extension(client):
    token = await _signup(client, "owner2@example.com")
    org_id = await _create_org(client, token)

    resp = await client.post(
        f"/api/orgs/{org_id}/knowledge/documents",
        files={"file": ("doc.xls", io.BytesIO(b"legacy"), "application/octet-stream")},
        data={"title": "Old doc"},
        headers=_auth(token),
    )
    assert resp.status_code == 400


async def test_update_document(client):
    token = await _signup(client, "owner3@example.com")
    org_id = await _create_org(client, token)
    resp = await client.post(
        f"/api/orgs/{org_id}/knowledge/documents",
        files=_fake_txt_file(),
        data={"title": "Draft title"},
        headers=_auth(token),
    )
    document_id = resp.json()["id"]

    resp = await client.patch(
        f"/api/orgs/{org_id}/knowledge/documents/{document_id}",
        json={"title": "Final title", "tags": ["Legal"]},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Final title"
    assert resp.json()["tags"] == ["Legal"]


async def test_replace_document_bumps_version(client):
    token = await _signup(client, "owner4@example.com")
    org_id = await _create_org(client, token)
    resp = await client.post(
        f"/api/orgs/{org_id}/knowledge/documents",
        files=_fake_txt_file(),
        data={"title": "Policy v1"},
        headers=_auth(token),
    )
    document_id = resp.json()["id"]

    resp = await client.post(
        f"/api/orgs/{org_id}/knowledge/documents/{document_id}/replace",
        files={"file": ("policy_v2.txt", io.BytesIO(b"Updated policy text."), "text/plain")},
        headers=_auth(token),
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["version"] == 2
    assert resp.json()["status"] == "processing"


async def test_delete_document(client):
    token = await _signup(client, "owner5@example.com")
    org_id = await _create_org(client, token)
    resp = await client.post(
        f"/api/orgs/{org_id}/knowledge/documents",
        files=_fake_txt_file(),
        data={"title": "To delete"},
        headers=_auth(token),
    )
    document_id = resp.json()["id"]

    resp = await client.delete(f"/api/orgs/{org_id}/knowledge/documents/{document_id}", headers=_auth(token))
    assert resp.status_code == 204

    resp = await client.get(f"/api/orgs/{org_id}/knowledge/documents/{document_id}", headers=_auth(token))
    assert resp.status_code == 404


async def test_responder_cannot_manage_knowledge_base(client, db_session):
    owner_token = await _signup(client, "owner6@example.com")
    org_id = await _create_org(client, owner_token)
    responder_token = await _add_member(client, db_session, org_id, "responder6@example.com", MembershipRole.responder)

    resp = await client.post(
        f"/api/orgs/{org_id}/knowledge/documents",
        files=_fake_txt_file(),
        data={"title": "Should fail"},
        headers=_auth(responder_token),
    )
    assert resp.status_code == 403


async def test_viewer_can_list_but_not_manage(client, db_session):
    owner_token = await _signup(client, "owner7@example.com")
    org_id = await _create_org(client, owner_token)
    await client.post(
        f"/api/orgs/{org_id}/knowledge/documents",
        files=_fake_txt_file(),
        data={"title": "Visible doc"},
        headers=_auth(owner_token),
    )
    viewer_token = await _add_member(client, db_session, org_id, "viewer7@example.com", MembershipRole.viewer)

    resp = await client.get(f"/api/orgs/{org_id}/knowledge/documents", headers=_auth(viewer_token))
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = await client.post(
        f"/api/orgs/{org_id}/knowledge/documents",
        files=_fake_txt_file(),
        data={"title": "Should fail"},
        headers=_auth(viewer_token),
    )
    assert resp.status_code == 403


async def test_knowledge_document_tenant_isolation(client):
    token_a = await _signup(client, "orga@example.com")
    org_a = await _create_org(client, token_a, "Org A")
    resp = await client.post(
        f"/api/orgs/{org_a}/knowledge/documents",
        files=_fake_txt_file(),
        data={"title": "Org A Policy"},
        headers=_auth(token_a),
    )
    document_id = resp.json()["id"]

    token_b = await _signup(client, "orgb@example.com")
    org_b = await _create_org(client, token_b, "Org B")

    resp = await client.get(f"/api/orgs/{org_a}/knowledge/documents", headers=_auth(token_b))
    assert resp.status_code == 403

    resp = await client.get(f"/api/orgs/{org_a}/knowledge/documents/{document_id}", headers=_auth(token_b))
    assert resp.status_code == 403

    resp = await client.patch(
        f"/api/orgs/{org_a}/knowledge/documents/{document_id}",
        json={"title": "hijacked"},
        headers=_auth(token_b),
    )
    assert resp.status_code == 403

    resp = await client.post(
        f"/api/orgs/{org_a}/knowledge/documents/{document_id}/replace",
        files=_fake_txt_file(),
        headers=_auth(token_b),
    )
    assert resp.status_code == 403

    resp = await client.delete(f"/api/orgs/{org_a}/knowledge/documents/{document_id}", headers=_auth(token_b))
    assert resp.status_code == 403

    # Stronger check (per the pattern established in Phase 1.4/1.5 reviews): a legitimate
    # member of org B, using their OWN org_id, must still 404 on org A's document_id — proving
    # the dual-filter query itself rejects it, not just the membership gate. Covers every
    # mutating route, not just GET.
    resp = await client.get(f"/api/orgs/{org_b}/knowledge/documents/{document_id}", headers=_auth(token_b))
    assert resp.status_code == 404

    resp = await client.patch(
        f"/api/orgs/{org_b}/knowledge/documents/{document_id}",
        json={"title": "hijacked via own org_id"},
        headers=_auth(token_b),
    )
    assert resp.status_code == 404

    resp = await client.post(
        f"/api/orgs/{org_b}/knowledge/documents/{document_id}/replace",
        files=_fake_txt_file(),
        headers=_auth(token_b),
    )
    assert resp.status_code == 404

    resp = await client.delete(f"/api/orgs/{org_b}/knowledge/documents/{document_id}", headers=_auth(token_b))
    assert resp.status_code == 404
