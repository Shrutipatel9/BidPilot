import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.rbac import assert_can_assign_role
from app.core.security import create_access_token, create_refresh_token, hash_password
from app.models.invitation import Invitation
from app.models.membership import Membership, MembershipRole
from app.models.organization import Organization
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.services import org_service
from app.services.audit_service import log_action
from app.services.email_service import dev_mode_no_smtp, send_email

_INVITATION_TTL = timedelta(days=7)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def create_invitation(
    db: AsyncSession,
    background_tasks: BackgroundTasks,
    org: Organization,
    inviter: Membership,
    email: str,
    role: MembershipRole,
) -> str | None:
    assert_can_assign_role(inviter.role, role)

    raw_token = secrets.token_urlsafe(32)
    invitation = Invitation(
        org_id=org.id,
        email=email,
        role=role,
        token_hash=_hash_token(raw_token),
        invited_by_user_id=inviter.user_id,
        expires_at=datetime.now(timezone.utc) + _INVITATION_TTL,
    )
    db.add(invitation)
    await log_action(db, org.id, inviter.user_id, "invitation.created", "invitation", email)
    await db.commit()

    accept_link = f"{settings.frontend_base_url}/accept-invitation?token={raw_token}"
    background_tasks.add_task(
        send_email,
        email,
        f"You've been invited to {org.name} on BidPilot",
        f"Accept your invite: {accept_link}",
    )
    return accept_link if dev_mode_no_smtp() else None


async def _get_invitation_by_token(db: AsyncSession, token: str) -> Invitation:
    result = await db.execute(select(Invitation).where(Invitation.token_hash == _hash_token(token)))
    invitation = result.scalar_one_or_none()
    if invitation is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "invitation not found")
    return invitation


async def preview_invitation(db: AsyncSession, token: str) -> tuple[Invitation, Organization, bool, bool]:
    invitation = await _get_invitation_by_token(db, token)
    org = await db.get(Organization, invitation.org_id)
    existing_user = await db.scalar(select(User).where(User.email == invitation.email))
    expired = invitation.expires_at < datetime.now(timezone.utc)
    requires_password = existing_user is None
    return invitation, org, requires_password, expired


async def accept_invitation(
    db: AsyncSession, token: str, password: str | None, name: str | None
) -> tuple[User, uuid.UUID, str, str]:
    invitation = await _get_invitation_by_token(db, token)

    if invitation.accepted_at is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "invitation already accepted")
    if invitation.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status.HTTP_410_GONE, "invitation expired")

    user = await db.scalar(select(User).where(User.email == invitation.email))
    if user is None:
        if not password:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "password is required to accept this invitation")
        user = User(
            email=invitation.email,
            hashed_password=hash_password(password),
            name=name,
            auth_provider="password",
            email_verified=True,  # proven by receiving/using the invite email
        )
        db.add(user)
        await db.flush()

    existing_membership = await db.scalar(
        select(Membership).where(Membership.org_id == invitation.org_id, Membership.user_id == user.id)
    )
    if existing_membership is not None:
        if existing_membership.role == MembershipRole.owner and invitation.role != MembershipRole.owner:
            # Same guard PATCH /api/orgs/{org_id}/members/{user_id} enforces — accepting a
            # re-invite must not be a backdoor around it.
            if await org_service.count_owners(db, invitation.org_id) <= 1:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "cannot demote the last remaining owner")
        existing_membership.role = invitation.role
    else:
        db.add(Membership(user_id=user.id, org_id=invitation.org_id, role=invitation.role))

    invitation.accepted_at = datetime.now(timezone.utc)
    await log_action(db, invitation.org_id, user.id, "invitation.accepted", "invitation", invitation.email)

    access_token = create_access_token(user.id)
    refresh_token, jti, expires_at = create_refresh_token(user.id)
    db.add(RefreshToken(id=jti, user_id=user.id, expires_at=expires_at))

    await db.commit()
    return user, invitation.org_id, access_token, refresh_token
