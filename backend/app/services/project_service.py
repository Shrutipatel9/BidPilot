import uuid
from datetime import date

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage import read_upload_capped, upload_bytes
from app.models.rfp_project import RfpProject
from app.services.audit_service import log_action

_ACCEPTED_EXTENSIONS = {"xlsx", "docx", "pdf"}
_CONTENT_TYPES = {
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pdf": "application/pdf",
}


def _extension_of(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in _ACCEPTED_EXTENSIONS:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"unsupported file type '.{ext}' — only .xlsx, .docx, and .pdf questionnaires are accepted",
        )
    return ext


async def create_project(
    db: AsyncSession,
    org_id: uuid.UUID,
    owner_id: uuid.UUID,
    name: str,
    buyer: str | None,
    due_date: date | None,
    tags: list[str],
    file: UploadFile,
) -> RfpProject:
    ext = _extension_of(file.filename or "")
    content = await read_upload_capped(file)

    project = RfpProject(
        org_id=org_id,
        name=name,
        buyer=buyer,
        due_date=due_date,
        owner_id=owner_id,
        source_file_key="",  # set below once we know the generated id
        source_file_ext=ext,
        tags=tags,
    )
    db.add(project)
    await db.flush()

    project.source_file_key = f"{org_id}/projects/{project.id}/source.{ext}"
    await upload_bytes(project.source_file_key, content, _CONTENT_TYPES[ext])

    await log_action(db, org_id, owner_id, "project.created", "rfp_project", str(project.id))
    await db.commit()
    await db.refresh(project)
    return project


async def list_projects(db: AsyncSession, org_id: uuid.UUID) -> list[RfpProject]:
    result = await db.execute(
        select(RfpProject).where(RfpProject.org_id == org_id).order_by(RfpProject.created_at.desc())
    )
    return list(result.scalars().all())


async def get_project(db: AsyncSession, org_id: uuid.UUID, project_id: uuid.UUID) -> RfpProject:
    result = await db.execute(
        select(RfpProject).where(RfpProject.org_id == org_id, RfpProject.id == project_id)
    )
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "project not found")
    return project
