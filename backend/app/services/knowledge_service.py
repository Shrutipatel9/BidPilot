import uuid
from datetime import date

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage import delete_object, read_upload_capped, upload_bytes
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import DocumentStatus, KnowledgeDocument
from app.services.audit_service import log_action
from app.workers.ingestion_tasks import ingest_document_task

_ACCEPTED_EXTENSIONS = {"pdf", "docx", "xlsx", "txt", "md"}
_CONTENT_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "txt": "text/plain",
    "md": "text/markdown",
}


def _extension_of(filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in _ACCEPTED_EXTENSIONS:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"unsupported file type '.{ext}' — only .pdf, .docx, .xlsx, .txt, and .md are accepted",
        )
    return ext


async def create_document(
    db: AsyncSession,
    org_id: uuid.UUID,
    owner_id: uuid.UUID,
    title: str,
    tags: list[str],
    review_date: date | None,
    file: UploadFile,
) -> KnowledgeDocument:
    ext = _extension_of(file.filename or "")
    content = await read_upload_capped(file)

    document = KnowledgeDocument(
        org_id=org_id,
        title=title,
        source_file_key="",
        source_file_ext=ext,
        tags=tags,
        review_date=review_date,
        owner_id=owner_id,
    )
    db.add(document)
    await db.flush()

    document.source_file_key = f"{org_id}/knowledge/{document.id}/source.{ext}"
    await upload_bytes(document.source_file_key, content, _CONTENT_TYPES[ext])

    await log_action(db, org_id, owner_id, "knowledge_document.created", "knowledge_document", str(document.id))
    await db.commit()
    await db.refresh(document)
    ingest_document_task.delay(str(document.id))
    return document


async def list_documents(db: AsyncSession, org_id: uuid.UUID) -> list[KnowledgeDocument]:
    result = await db.execute(
        select(KnowledgeDocument).where(KnowledgeDocument.org_id == org_id).order_by(KnowledgeDocument.created_at.desc())
    )
    return list(result.scalars().all())


async def get_document(db: AsyncSession, org_id: uuid.UUID, document_id: uuid.UUID) -> KnowledgeDocument:
    result = await db.execute(
        select(KnowledgeDocument).where(KnowledgeDocument.org_id == org_id, KnowledgeDocument.id == document_id)
    )
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "knowledge document not found")
    return document


async def update_document(
    db: AsyncSession,
    document: KnowledgeDocument,
    title: str | None,
    tags: list[str] | None,
    review_date: date | None,
) -> KnowledgeDocument:
    if title is not None:
        document.title = title
    if tags is not None:
        document.tags = tags
    if review_date is not None:
        document.review_date = review_date
    await db.commit()
    await db.refresh(document)
    return document


async def replace_document(
    db: AsyncSession, document: KnowledgeDocument, actor_id: uuid.UUID, file: UploadFile
) -> KnowledgeDocument:
    ext = _extension_of(file.filename or "")
    content = await read_upload_capped(file)

    await db.execute(delete(KnowledgeChunk).where(KnowledgeChunk.document_id == document.id))
    document.source_file_ext = ext
    document.source_file_key = f"{document.org_id}/knowledge/{document.id}/source.{ext}"
    document.version += 1
    document.status = DocumentStatus.processing
    await upload_bytes(document.source_file_key, content, _CONTENT_TYPES[ext])

    await log_action(db, document.org_id, actor_id, "knowledge_document.replaced", "knowledge_document", str(document.id))
    await db.commit()
    await db.refresh(document)
    return document


async def delete_document(db: AsyncSession, document: KnowledgeDocument, actor_id: uuid.UUID) -> None:
    await db.execute(delete(KnowledgeChunk).where(KnowledgeChunk.document_id == document.id))
    await delete_object(document.source_file_key)
    await log_action(db, document.org_id, actor_id, "knowledge_document.deleted", "knowledge_document", str(document.id))
    await db.delete(document)
    await db.commit()
