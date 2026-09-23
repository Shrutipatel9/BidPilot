import uuid

from app.models.membership import Membership, MembershipRole
from app.models.user import User


async def _signup(client, email, password="correct-horse-battery"):
    resp = await client.post("/api/auth/signup", json={"email": email, "password": password})
    body = resp.json()
    return body["user"]["id"], body["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


async def test_create_and_list_organization(client):
    _, token = await _signup(client, "owner1@example.com")

    resp = await client.post("/api/orgs", json={"name": "Acme Inc"}, headers=_auth(token))
    assert resp.status_code == 201, resp.text
    org_id = resp.json()["id"]

    resp = await client.get("/api/orgs", headers=_auth(token))
    assert resp.status_code == 200
    assert any(o["id"] == org_id for o in resp.json())


async def test_member_role_change_and_last_owner_guard(client, db_session):
    owner_id, owner_token = await _signup(client, "owner2@example.com")
    org_resp = await client.post("/api/orgs", json={"name": "Acme Inc"}, headers=_auth(owner_token))
    org_id = org_resp.json()["id"]

    # Add a second member directly (invitation flow is tested separately).
    other_user = User(email="member2@example.com", hashed_password="x", auth_provider="password")
    db_session.add(other_user)
    await db_session.flush()
    db_session.add(Membership(user_id=other_user.id, org_id=org_id, role=MembershipRole.reviewer))
    await db_session.commit()

    resp = await client.patch(
        f"/api/orgs/{org_id}/members/{other_user.id}", json={"role": "admin"}, headers=_auth(owner_token)
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["role"] == "admin"

    # The owner is the only owner — demoting them must be rejected.
    resp = await client.patch(
        f"/api/orgs/{org_id}/members/{owner_id}", json={"role": "admin"}, headers=_auth(owner_token)
    )
    assert resp.status_code == 400


async def test_admin_cannot_grant_owner_role_via_role_change(client, db_session):
    owner_id, owner_token = await _signup(client, "owner-esc@example.com")
    org_resp = await client.post("/api/orgs", json={"name": "Acme Inc"}, headers=_auth(owner_token))
    org_id = org_resp.json()["id"]

    admin_id, admin_token = await _signup(client, "admin-esc@example.com")
    db_session.add(Membership(user_id=uuid.UUID(admin_id), org_id=org_id, role=MembershipRole.admin))
    await db_session.commit()

    # Admin cannot self-promote to owner...
    resp = await client.patch(
        f"/api/orgs/{org_id}/members/{admin_id}", json={"role": "owner"}, headers=_auth(admin_token)
    )
    assert resp.status_code == 403

    # ...nor grant owner to anyone else, e.g. demoting the real owner's status by "sharing" it.
    resp = await client.patch(
        f"/api/orgs/{org_id}/members/{owner_id}", json={"role": "owner"}, headers=_auth(admin_token)
    )
    assert resp.status_code == 403


async def test_non_member_cannot_view_members(client):
    _, owner_token = await _signup(client, "owner3@example.com")
    org_resp = await client.post("/api/orgs", json={"name": "Acme Inc"}, headers=_auth(owner_token))
    org_id = org_resp.json()["id"]

    _, outsider_token = await _signup(client, "outsider@example.com")
    resp = await client.get(f"/api/orgs/{org_id}/members", headers=_auth(outsider_token))
    assert resp.status_code == 403
