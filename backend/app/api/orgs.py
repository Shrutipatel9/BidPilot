import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.core.rbac import assert_can_assign_role, get_membership, require_role
from app.db.session import get_db
from app.models.audit_log import AuditLog
from app.models.membership import Membership, MembershipRole
from app.models.user import User
from app.schemas.org import (
    AuditLogEntryResponse,
    ChangeRoleRequest,
    CreateOrganizationRequest,
    MemberResponse,
    OrganizationResponse,
)
from app.services import org_service
from app.services.audit_service import log_action

router = APIRouter(prefix="/api/orgs", tags=["orgs"])


@router.post("", response_model=OrganizationResponse, status_code=201)
async def create_organization(
    body: CreateOrganizationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    org = await org_service.create_organization(db, current_user.id, body.name)
    return OrganizationResponse.model_validate(org)


@router.get("", response_model=list[OrganizationResponse])
async def list_my_organizations(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    orgs = await org_service.list_my_organizations(db, current_user.id)
    return [OrganizationResponse.model_validate(o) for o in orgs]


@router.get("/{org_id}/members", response_model=list[MemberResponse])
async def list_members(
    org_id: uuid.UUID,
    membership: Membership = Depends(get_membership),  # any member of the org may view
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Membership, User).join(User, User.id == Membership.user_id).where(Membership.org_id == org_id)
    )
    return [
        MemberResponse(user_id=user.id, email=user.email, name=user.name, role=membership_row.role)
        for membership_row, user in result.all()
    ]


@router.patch("/{org_id}/members/{user_id}", response_model=MemberResponse)
async def change_member_role(
    org_id: uuid.UUID,
    user_id: uuid.UUID,
    body: ChangeRoleRequest,
    membership: Membership = Depends(require_role(MembershipRole.owner, MembershipRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Membership, User).join(User, User.id == Membership.user_id).where(
            Membership.org_id == org_id, Membership.user_id == user_id
        )
    )
    row = result.first()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "member not found")
    target_membership, target_user = row

    assert_can_assign_role(membership.role, body.role)

    if target_membership.role == MembershipRole.owner and body.role != MembershipRole.owner:
        if await org_service.count_owners(db, org_id) <= 1:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "cannot demote the last remaining owner")

    target_membership.role = body.role
    await log_action(db, org_id, membership.user_id, "member.role_changed", "membership", str(user_id))
    await db.commit()

    return MemberResponse(user_id=target_user.id, email=target_user.email, name=target_user.name, role=body.role)


@router.get("/{org_id}/audit-log", response_model=list[AuditLogEntryResponse])
async def get_audit_log(
    org_id: uuid.UUID,
    membership: Membership = Depends(require_role(MembershipRole.owner, MembershipRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AuditLog).where(AuditLog.org_id == org_id).order_by(AuditLog.timestamp.desc())
    )
    return [AuditLogEntryResponse.model_validate(entry) for entry in result.scalars().all()]
