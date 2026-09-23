import enum
import uuid
from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import TimestampMixin


class ProjectStatus(str, enum.Enum):
    uploaded = "uploaded"
    questions_confirmed = "questions_confirmed"
    drafting = "drafting"
    drafted = "drafted"


class RfpProject(TimestampMixin, Base):
    __tablename__ = "rfp_projects"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    buyer: Mapped[str | None] = mapped_column(String(255), default=None)
    due_date: Mapped[date | None] = mapped_column(Date, default=None)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status"), default=ProjectStatus.uploaded, nullable=False
    )
    owner_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), default=None)
    source_file_key: Mapped[str] = mapped_column(String(512), nullable=False)
    source_file_ext: Mapped[str] = mapped_column(String(10), nullable=False)
    tags: Mapped[list] = mapped_column(JSONB, default=list, nullable=False)
