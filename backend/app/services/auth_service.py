import uuid
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_purpose_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
    verify_purpose_token,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.services.audit_service import log_action
from app.services.email_service import dev_mode_no_smtp, send_email

_INVALID_CREDENTIALS = HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid email or password")
_INVALID_TOKEN = HTTPException(status.HTTP_400_BAD_REQUEST, "invalid or expired token")


async def _issue_tokens(db: AsyncSession, user_id: uuid.UUID) -> tuple[str, str]:
    access_token = create_access_token(user_id)
    refresh_token, jti, expires_at = create_refresh_token(user_id)
    db.add(RefreshToken(id=jti, user_id=user_id, expires_at=expires_at))
    await db.commit()
    return access_token, refresh_token


async def signup(
    db: AsyncSession, background_tasks: BackgroundTasks, email: str, password: str, name: str | None
) -> tuple[User, str, str, str | None]:
    existing = await db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "an account with this email already exists")

    user = User(
        email=email,
        hashed_password=hash_password(password),
        name=name,
        auth_provider="password",
        email_verified=False,
    )
    db.add(user)
    await db.flush()

    verify_token = create_purpose_token(user.id, "email_verify", timedelta(hours=24))
    verify_link = f"{settings.frontend_base_url}/verify-email?token={verify_token}"
    # Backgrounded — an SMTP round-trip (real-world: 1-5s) must never add latency to the
    # signup response the user is waiting on.
    background_tasks.add_task(
        send_email, user.email, "Verify your BidPilot email", f"Verify your email: {verify_link}"
    )

    await log_action(db, None, user.id, "user.signed_up", "user", str(user.id))
    access_token, refresh_token = await _issue_tokens(db, user.id)
    debug_link = verify_link if dev_mode_no_smtp() else None
    return user, access_token, refresh_token, debug_link


async def login(db: AsyncSession, email: str, password: str) -> tuple[User, str, str]:
    user = await db.scalar(select(User).where(User.email == email))
    if user is None or user.hashed_password is None or not verify_password(password, user.hashed_password):
        raise _INVALID_CREDENTIALS

    await log_action(db, None, user.id, "user.logged_in", "user", str(user.id))
    access_token, refresh_token = await _issue_tokens(db, user.id)
    return user, access_token, refresh_token


async def refresh(db: AsyncSession, refresh_token_str: str) -> tuple[str, str]:
    try:
        payload = decode_token(refresh_token_str)
    except jwt.PyJWTError:
        raise _INVALID_CREDENTIALS

    if payload.get("type") != "refresh":
        raise _INVALID_CREDENTIALS

    try:
        jti = uuid.UUID(payload["jti"])
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError):
        raise _INVALID_CREDENTIALS

    token_row = await db.get(RefreshToken, jti)
    if token_row is None:
        raise _INVALID_CREDENTIALS
    if token_row.revoked_at is not None:
        # Reuse of an already-rotated-out refresh token — a theft/replay signal, worth its own record.
        await log_action(db, None, user_id, "refresh_token.reuse_detected", "refresh_token", str(jti))
        await db.commit()
        raise _INVALID_CREDENTIALS
    if token_row.expires_at < datetime.now(timezone.utc):
        raise _INVALID_CREDENTIALS

    new_access_token = create_access_token(user_id)
    new_refresh_token, new_jti, new_expires_at = create_refresh_token(user_id)

    # New row must exist before the old row's FK (replaced_by_id) can point at it.
    db.add(RefreshToken(id=new_jti, user_id=user_id, expires_at=new_expires_at))
    await db.flush()

    token_row.revoked_at = datetime.now(timezone.utc)
    token_row.replaced_by_id = new_jti
    await db.commit()

    return new_access_token, new_refresh_token


async def request_password_reset(db: AsyncSession, background_tasks: BackgroundTasks, email: str) -> str | None:
    user = await db.scalar(select(User).where(User.email == email))
    if user is None:
        return None  # don't reveal whether the email exists

    reset_token = create_purpose_token(
        user.id, "password_reset", timedelta(minutes=30), token_version=user.token_version
    )
    reset_link = f"{settings.frontend_base_url}/reset-password?token={reset_token}"
    background_tasks.add_task(
        send_email, user.email, "Reset your BidPilot password", f"Reset your password: {reset_link}"
    )
    return reset_link if dev_mode_no_smtp() else None


async def reset_password(db: AsyncSession, token: str, new_password: str) -> None:
    try:
        payload = verify_purpose_token(token, "password_reset")
    except (jwt.PyJWTError, ValueError):
        raise _INVALID_TOKEN

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError):
        raise _INVALID_TOKEN

    user = await db.get(User, user_id)
    if user is None or payload.get("tv") != user.token_version:
        raise _INVALID_TOKEN

    user.hashed_password = hash_password(new_password)
    user.token_version += 1  # burns this token and any other outstanding reset link
    await db.commit()


async def verify_email(db: AsyncSession, token: str) -> None:
    try:
        payload = verify_purpose_token(token, "email_verify")
    except (jwt.PyJWTError, ValueError):
        raise _INVALID_TOKEN

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError):
        raise _INVALID_TOKEN

    user = await db.get(User, user_id)
    if user is None:
        raise _INVALID_TOKEN

    user.email_verified = True
    await db.commit()
