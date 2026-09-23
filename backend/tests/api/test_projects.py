import io


async def _signup(client, email, password="correct-horse-battery"):
    resp = await client.post("/api/auth/signup", json={"email": email, "password": password})
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


async def _create_org(client, token, name="Acme Inc"):
    resp = await client.post("/api/orgs", json={"name": name}, headers=_auth(token))
    return resp.json()["id"]


def _fake_xlsx_file():
    return {"file": ("questionnaire.xlsx", io.BytesIO(b"fake xlsx bytes"), "application/octet-stream")}


async def test_create_and_list_project(client):
    token = await _signup(client, "owner1@example.com")
    org_id = await _create_org(client, token)

    resp = await client.post(
        f"/api/orgs/{org_id}/projects",
        files=_fake_xlsx_file(),
        data={"name": "Acme Security Questionnaire", "buyer": "Acme Corp"},
        headers=_auth(token),
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["name"] == "Acme Security Questionnaire"
    assert body["status"] == "uploaded"
    assert body["source_file_ext"] == "xlsx"

    resp = await client.get(f"/api/orgs/{org_id}/projects", headers=_auth(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = await client.get(f"/api/orgs/{org_id}/projects/{body['id']}", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["id"] == body["id"]


async def test_reject_unsupported_extension(client):
    token = await _signup(client, "owner2@example.com")
    org_id = await _create_org(client, token)

    resp = await client.post(
        f"/api/orgs/{org_id}/projects",
        files={"file": ("questionnaire.txt", io.BytesIO(b"hi"), "text/plain")},
        data={"name": "Bad File"},
        headers=_auth(token),
    )
    assert resp.status_code == 400


async def test_viewer_cannot_create_project(client, db_session):
    import uuid

    from app.models.membership import Membership, MembershipRole

    owner_token = await _signup(client, "owner3@example.com")
    org_id = await _create_org(client, owner_token)

    viewer_token = await _signup(client, "viewer3@example.com")
    me = await client.get("/api/auth/me", headers=_auth(viewer_token))
    db_session.add(
        Membership(user_id=uuid.UUID(me.json()["id"]), org_id=uuid.UUID(org_id), role=MembershipRole.viewer)
    )
    await db_session.commit()

    resp = await client.post(
        f"/api/orgs/{org_id}/projects",
        files=_fake_xlsx_file(),
        data={"name": "Should Fail"},
        headers=_auth(viewer_token),
    )
    assert resp.status_code == 403


async def test_project_tenant_isolation(client):
    token_a = await _signup(client, "orga-owner@example.com")
    org_a = await _create_org(client, token_a, "Org A")
    resp = await client.post(
        f"/api/orgs/{org_a}/projects",
        files=_fake_xlsx_file(),
        data={"name": "Org A Project"},
        headers=_auth(token_a),
    )
    project_id = resp.json()["id"]

    token_b = await _signup(client, "orgb-owner@example.com")
    org_b = await _create_org(client, token_b, "Org B")

    resp = await client.get(f"/api/orgs/{org_a}/projects", headers=_auth(token_b))
    assert resp.status_code == 403

    resp = await client.get(f"/api/orgs/{org_a}/projects/{project_id}", headers=_auth(token_b))
    assert resp.status_code == 403
