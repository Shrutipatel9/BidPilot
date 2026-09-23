import uuid

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.membership import Membership, MembershipRole
from app.models.user import User

_FORBIDDEN = HTTPException(status.HTTP_403_FORBIDDEN, "not a member of this organization")


async def get_membership(
    org_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Membership:
    """org_id is resolved from the route's path parameter — FastAPI binds it by name across
    the dependency tree, so it can never come from the request body/query here."""
    result = await db.execute(
        select(Membership).where(Membership.org_id == org_id, Membership.user_id == current_user.id)
    )
    membership = result.scalar_one_or_none()
    if membership is None:
        raise _FORBIDDEN
    return membership


def require_role(*allowed: MembershipRole):
    async def dependency(membership: Membership = Depends(get_membership)) -> Membership:
        if membership.role not in allowed:
            # Same 403 as "not a member" — don't let a 404-vs-403 split leak org existence
            # or membership status to someone who isn't authorized either way.
            raise _FORBIDDEN
        return membership

    return dependency


def assert_can_assign_role(assigner_role: MembershipRole, target_role: MembershipRole) -> None:
    """The one role-ceiling rule in the system: an Admin can grant any role except Owner.
    Applies everywhere a role gets assigned or changed — invitations and direct role edits
    alike — so granting Owner always requires actually being an Owner."""
    if assigner_role == MembershipRole.admin and target_role == MembershipRole.owner:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "admins cannot grant the owner role")
