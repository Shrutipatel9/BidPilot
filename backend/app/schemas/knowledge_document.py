import uuid
from datetime import date, datetime

from pydantic import BaseModel

from app.models.knowledge_document import DocumentStatus


class KnowledgeDocumentResponse(BaseModel):
    id: uuid.UUID
    org_id: uuid.UUID
    title: str
    source_file_ext: str
    tags: list[str]
    review_date: date | None
    status: DocumentStatus
    version: int
    owner_id: uuid.UUID | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UpdateKnowledgeDocumentRequest(BaseModel):
    title: str | None = None
    tags: list[str] | None = None
    review_date: date | None = None
