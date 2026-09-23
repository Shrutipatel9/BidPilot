from pydantic import BaseModel, EmailStr, Field

from app.models.membership import MembershipRole


class CreateInvitationRequest(BaseModel):
    email: EmailStr
    role: MembershipRole


class CreateInvitationResponse(BaseModel):
    message: str
    debug_link: str | None = None


class InvitationPreviewResponse(BaseModel):
    email: EmailStr
    org_name: str
    role: MembershipRole
    requires_password: bool
    expired: bool


class AcceptInvitationRequest(BaseModel):
    password: str | None = Field(default=None, min_length=8, max_length=72)
    name: str | None = None
