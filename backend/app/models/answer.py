import enum
import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class AnswerStatus(str, enum.Enum):
    not_started = "not_started"
    ai_drafted = "ai_drafted"
    needs_review = "needs_review"
    in_review = "in_review"
    approved = "approved"
    rejected = "rejected"


class Answer(TimestampMixin, Base):
    __tablename__ = "answers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE"), unique=True, index=True, nullable=False
    )
    text: Mapped[str] = mapped_column(String, default="", nullable=False)
    choice: Mapped[str | None] = mapped_column(String(255), default=None)
    confidence: Mapped[int | None] = mapped_column(Integer, default=None)
    citations: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
    status: Mapped[AnswerStatus] = mapped_column(
        Enum(AnswerStatus, name="answer_status"), default=AnswerStatus.not_started, nullable=False
    )
    assignee_user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), default=None
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
