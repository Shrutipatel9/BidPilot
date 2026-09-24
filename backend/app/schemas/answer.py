import uuid

from pydantic import BaseModel

from app.models.answer import AnswerStatus


class AnswerResponse(BaseModel):
    id: uuid.UUID
    question_id: uuid.UUID
    text: str
    choice: str | None
    confidence: int | None
    status: AnswerStatus
    version: int

    model_config = {"from_attributes": True}
