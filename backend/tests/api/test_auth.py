from urllib.parse import parse_qs, urlparse


def _token_from_link(link: str) -> str:
    return parse_qs(urlparse(link).query)["token"][0]


async def test_signup_verify_login_flow(client):
    resp = await client.post(
        "/api/auth/signup", json={"email": "alice@example.com", "password": "correct-horse", "name": "Alice"}
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["user"]["email"] == "alice@example.com"
    assert body["user"]["email_verified"] is False
    assert body["debug_link"] is not None  # dev mode, no SMTP configured

    verify_token = _token_from_link(body["debug_link"])
    resp = await client.post("/api/auth/verify-email", json={"token": verify_token})
    assert resp.status_code == 200, resp.text

    resp = await client.post("/api/auth/login", json={"email": "alice@example.com", "password": "correct-horse"})
    assert resp.status_code == 200, resp.text
    tokens = resp.json()
    assert tokens["access_token"] and tokens["refresh_token"]

    resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert resp.status_code == 200, resp.text
    assert resp.json()["email_verified"] is True


async def test_login_wrong_password_rejected(client):
    await client.post("/api/auth/signup", json={"email": "bob@example.com", "password": "correct-horse"})
    resp = await client.post("/api/auth/login", json={"email": "bob@example.com", "password": "wrong-password"})
    assert resp.status_code == 401


async def test_duplicate_signup_email_rejected(client):
    await client.post("/api/auth/signup", json={"email": "carol@example.com", "password": "correct-horse"})
    resp = await client.post("/api/auth/signup", json={"email": "carol@example.com", "password": "another-pass"})
    assert resp.status_code == 409


async def test_refresh_rotation_rejects_old_token(client):
    signup = await client.post(
        "/api/auth/signup", json={"email": "dave@example.com", "password": "correct-horse"}
    )
    old_refresh = signup.json()["refresh_token"]

    resp = await client.post("/api/auth/refresh", json={"refresh_token": old_refresh})
    assert resp.status_code == 200, resp.text
    new_refresh = resp.json()["refresh_token"]
    assert new_refresh != old_refresh

    # Reusing the rotated-out refresh token must fail.
    resp = await client.post("/api/auth/refresh", json={"refresh_token": old_refresh})
    assert resp.status_code == 401

    # The new one must still work.
    resp = await client.post("/api/auth/refresh", json={"refresh_token": new_refresh})
    assert resp.status_code == 200


async def test_password_reset_flow_invalidates_link_after_use(client):
    await client.post("/api/auth/signup", json={"email": "erin@example.com", "password": "old-password"})

    resp = await client.post("/api/auth/request-password-reset", json={"email": "erin@example.com"})
    assert resp.status_code == 200
    reset_link = resp.json()["debug_link"]
    assert reset_link is not None
    reset_token = _token_from_link(reset_link)

    resp = await client.post(
        "/api/auth/reset-password", json={"token": reset_token, "new_password": "new-password"}
    )
    assert resp.status_code == 200, resp.text

    # Old password no longer works, new one does.
    resp = await client.post("/api/auth/login", json={"email": "erin@example.com", "password": "old-password"})
    assert resp.status_code == 401
    resp = await client.post("/api/auth/login", json={"email": "erin@example.com", "password": "new-password"})
    assert resp.status_code == 200

    # Reusing the same reset link a second time must fail (token_version already bumped).
    resp = await client.post(
        "/api/auth/reset-password", json={"token": reset_token, "new_password": "another-password"}
    )
    assert resp.status_code == 400


async def test_password_reset_unknown_email_does_not_leak(client):
    resp = await client.post("/api/auth/request-password-reset", json={"email": "nobody@example.com"})
    assert resp.status_code == 200
    assert resp.json()["debug_link"] is None
