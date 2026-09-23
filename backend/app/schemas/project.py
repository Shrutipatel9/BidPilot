import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.rfp_project import ProjectStatus


class ProjectResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    name: str
    buyer: str | None
    due_date: date | None
    status: ProjectStatus
    owner_id: uuid.UUID | None
    source_file_ext: str
    tags: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}
