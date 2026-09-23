"""Mandatory per docs/testing.md §2: a user in one org must never be able to read or write
another org's data, even with a valid access token. See docs/architecture.md §9."""


async def _signup(client, email, password="correct-horse-battery"):
    resp = await client.post("/api/auth/signup", json={"email": email, "password": password})
    return resp.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


async def _create_org(client, token, name):
    resp = await client.post("/api/orgs", json={"name": name}, headers=_auth(token))
    return resp.json()["id"]


async def test_user_cannot_read_another_orgs_members(client):
    token_a = await _signup(client, "orga-owner@example.com")
    org_a = await _create_org(client, token_a, "Org A")

    token_b = await _signup(client, "orgb-owner@example.com")
    await _create_org(client, token_b, "Org B")

    resp = await client.get(f"/api/orgs/{org_a}/members", headers=_auth(token_b))
    assert resp.status_code == 403


async def test_user_cannot_read_another_orgs_audit_log(client):
    token_a = await _signup(client, "orga-owner2@example.com")
    org_a = await _create_org(client, token_a, "Org A")

    token_b = await _signup(client, "orgb-owner2@example.com")
    await _create_org(client, token_b, "Org B")

    resp = await client.get(f"/api/orgs/{org_a}/audit-log", headers=_auth(token_b))
    assert resp.status_code == 403


async def test_user_cannot_change_role_in_another_org(client):
    token_a = await _signup(client, "orga-owner3@example.com")
    org_a = await _create_org(client, token_a, "Org A")

    token_b = await _signup(client, "orgb-owner3@example.com")
    await _create_org(client, token_b, "Org B")

    # Org B's owner tries to change Org A's owner's role.
    me_a = await client.get("/api/auth/me", headers=_auth(token_a))
    user_a_id = me_a.json()["id"]

    resp = await client.patch(
        f"/api/orgs/{org_a}/members/{user_a_id}", json={"role": "viewer"}, headers=_auth(token_b)
    )
    assert resp.status_code == 403


async def test_user_cannot_invite_into_another_org(client):
    token_a = await _signup(client, "orga-owner4@example.com")
    org_a = await _create_org(client, token_a, "Org A")

    token_b = await _signup(client, "orgb-owner4@example.com")
    await _create_org(client, token_b, "Org B")

    resp = await client.post(
        f"/api/orgs/{org_a}/invitations",
        json={"email": "sneaky@example.com", "role": "admin"},
        headers=_auth(token_b),
    )
    assert resp.status_code == 403
