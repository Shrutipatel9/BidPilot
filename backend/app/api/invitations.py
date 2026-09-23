import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import require_role
from app.db.session import get_db
from app.models.membership import Membership, MembershipRole
from app.models.organization import Organization
from app.schemas.auth import TokenResponse
from app.schemas.invitation import (
    AcceptInvitationRequest,
    CreateInvitationRequest,
    CreateInvitationResponse,
    InvitationPreviewResponse,
)
from app.services import invitation_service

router = APIRouter(tags=["invitations"])


@router.post("/api/orgs/{org_id}/invitations", response_model=CreateInvitationResponse, status_code=201)
async def create_invitation(
    org_id: uuid.UUID,
    body: CreateInvitationRequest,
    membership: Membership = Depends(require_role(MembershipRole.owner, MembershipRole.admin)),
    db: AsyncSession = Depends(get_db),
):
    org = await db.get(Organization, org_id)
    debug_link = await invitation_service.create_invitation(db, org, membership, body.email, body.role)
    return CreateInvitationResponse(message="invitation sent", debug_link=debug_link)


@router.get("/api/invitations/{token}", response_model=InvitationPreviewResponse)
async def preview_invitation(token: str, db: AsyncSession = Depends(get_db)):
    invitation, org, requires_password, expired = await invitation_service.preview_invitation(db, token)
    return InvitationPreviewResponse(
        email=invitation.email,
        org_name=org.name,
        role=invitation.role,
        requires_password=requires_password,
        expired=expired,
    )


@router.post("/api/invitations/{token}/accept", response_model=TokenResponse)
async def accept_invitation(token: str, body: AcceptInvitationRequest, db: AsyncSession = Depends(get_db)):
    _, _, access_token, refresh_token = await invitation_service.accept_invitation(
        db, token, body.password, body.name
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)
