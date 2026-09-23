import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.membership import MembershipRole


class CreateOrganizationRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class OrganizationResponse(BaseModel):
    id: uuid.UUID
    name: str
    plan: str

    model_config = {"from_attributes": True}


class MemberResponse(BaseModel):
    user_id: uuid.UUID
    email: str
    name: str | None
    role: MembershipRole


class ChangeRoleRequest(BaseModel):
    role: MembershipRole


class AuditLogEntryResponse(BaseModel):
    id: uuid.UUID
    actor_user_id: uuid.UUID | None
    action: str
    entity_type: str
    entity_id: str | None
    timestamp: datetime

    model_config = {"from_attributes": True}
