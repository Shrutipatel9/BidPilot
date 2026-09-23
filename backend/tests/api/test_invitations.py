from urllib.parse import parse_qs, urlparse


def _token_from_link(link: str) -> str:
    return parse_qs(urlparse(link).query)["token"][0]


async def _signup(client, email, password="correct-horse-battery"):
    resp = await client.post("/api/auth/signup", json={"email": email, "password": password})
    body = resp.json()
    return body["user"]["id"], body["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


async def _create_org(client, token, name="Acme Inc"):
    resp = await client.post("/api/orgs", json={"name": name}, headers=_auth(token))
    return resp.json()["id"]


async def test_new_user_invite_preview_and_accept(client):
    _, owner_token = await _signup(client, "owner-inv1@example.com")
    org_id = await _create_org(client, owner_token)

    resp = await client.post(
        f"/api/orgs/{org_id}/invitations",
        json={"email": "newbie@example.com", "role": "reviewer"},
        headers=_auth(owner_token),
    )
    assert resp.status_code == 201, resp.text
    invite_token = _token_from_link(resp.json()["debug_link"])

    preview = await client.get(f"/api/invitations/{invite_token}")
    assert preview.status_code == 200
    assert preview.json()["requires_password"] is True
    assert preview.json()["role"] == "reviewer"

    accept = await client.post(
        f"/api/invitations/{invite_token}/accept", json={"password": "another-horse-battery"}
    )
    assert accept.status_code == 200, accept.text

    members = await client.get(f"/api/orgs/{org_id}/members", headers=_auth(owner_token))
    emails = {m["email"]: m["role"] for m in members.json()}
    assert emails["newbie@example.com"] == "reviewer"


async def test_existing_user_invite_accept_needs_no_password(client):
    _, owner_token = await _signup(client, "owner-inv2@example.com")
    _, _ = await _signup(client, "existing@example.com")
    org_id = await _create_org(client, owner_token)

    resp = await client.post(
        f"/api/orgs/{org_id}/invitations",
        json={"email": "existing@example.com", "role": "responder"},
        headers=_auth(owner_token),
    )
    invite_token = _token_from_link(resp.json()["debug_link"])

    preview = await client.get(f"/api/invitations/{invite_token}")
    assert preview.json()["requires_password"] is False

    accept = await client.post(f"/api/invitations/{invite_token}/accept", json={})
    assert accept.status_code == 200, accept.text


async def test_invitation_cannot_be_accepted_twice(client):
    _, owner_token = await _signup(client, "owner-inv3@example.com")
    org_id = await _create_org(client, owner_token)

    resp = await client.post(
        f"/api/orgs/{org_id}/invitations",
        json={"email": "onceonly@example.com", "role": "viewer"},
        headers=_auth(owner_token),
    )
    invite_token = _token_from_link(resp.json()["debug_link"])

    first = await client.post(f"/api/invitations/{invite_token}/accept", json={"password": "correct-horse-1"})
    assert first.status_code == 200

    second = await client.post(f"/api/invitations/{invite_token}/accept", json={"password": "correct-horse-2"})
    assert second.status_code == 409


async def test_admin_cannot_invite_owner(client):
    _, owner_token = await _signup(client, "owner-inv4@example.com")
    org_id = await _create_org(client, owner_token)

    resp = await client.post(
        f"/api/orgs/{org_id}/invitations",
        json={"email": "future-admin@example.com", "role": "admin"},
        headers=_auth(owner_token),
    )
    admin_invite_token = _token_from_link(resp.json()["debug_link"])
    accept = await client.post(
        f"/api/invitations/{admin_invite_token}/accept", json={"password": "correct-horse-3"}
    )
    admin_token = accept.json()["access_token"]

    resp = await client.post(
        f"/api/orgs/{org_id}/invitations",
        json={"email": "wannabe-owner@example.com", "role": "owner"},
        headers=_auth(admin_token),
    )
    assert resp.status_code == 403


async def test_accepting_reinvite_cannot_demote_last_owner(client):
    # Re-inviting the sole owner's own email to a lower role, then accepting it, must be
    # blocked the same way a direct role-change would be — accept-invitation isn't a backdoor
    # around the last-owner guard.
    owner_id, owner_token = await _signup(client, "sole-owner@example.com")
    org_id = await _create_org(client, owner_token)

    resp = await client.post(
        f"/api/orgs/{org_id}/invitations",
        json={"email": "sole-owner@example.com", "role": "viewer"},
        headers=_auth(owner_token),
    )
    assert resp.status_code == 201, resp.text
    invite_token = _token_from_link(resp.json()["debug_link"])

    accept = await client.post(f"/api/invitations/{invite_token}/accept", json={})
    assert accept.status_code == 400, accept.text

    members = await client.get(f"/api/orgs/{org_id}/members", headers=_auth(owner_token))
    roles = {m["email"]: m["role"] for m in members.json()}
    assert roles["sole-owner@example.com"] == "owner"
