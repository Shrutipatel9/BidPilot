import json
import uuid
from datetime import date

from fastapi import APIRouter, Depends, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import get_membership, require_role
from app.db.session import get_db
from app.models.membership import Membership, MembershipRole
from app.schemas.knowledge_document import KnowledgeDocumentResponse, UpdateKnowledgeDocumentRequest
from app.services import knowledge_service

router = APIRouter(prefix="/api/orgs/{org_id}/knowledge", tags=["knowledge"])

_KB_MANAGE_ROLES = (MembershipRole.owner, MembershipRole.admin, MembershipRole.knowledge_manager)


@router.post("/documents", response_model=KnowledgeDocumentResponse, status_code=201)
async def create_document(
    org_id: uuid.UUID,
    file: UploadFile,
    title: str = Form(...),
    tags: str = Form("[]"),
    review_date: date | None = Form(None),
    membership: Membership = Depends(require_role(*_KB_MANAGE_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    document = await knowledge_service.create_document(
        db, org_id, membership.user_id, title, json.loads(tags), review_date, file
    )
    return KnowledgeDocumentResponse.model_validate(document)


@router.get("/documents", response_model=list[KnowledgeDocumentResponse])
async def list_documents(
    org_id: uuid.UUID,
    membership: Membership = Depends(get_membership),
    db: AsyncSession = Depends(get_db),
):
    documents = await knowledge_service.list_documents(db, org_id)
    return [KnowledgeDocumentResponse.model_validate(d) for d in documents]


@router.get("/documents/{document_id}", response_model=KnowledgeDocumentResponse)
async def get_document(
    org_id: uuid.UUID,
    document_id: uuid.UUID,
    membership: Membership = Depends(get_membership),
    db: AsyncSession = Depends(get_db),
):
    document = await knowledge_service.get_document(db, org_id, document_id)
    return KnowledgeDocumentResponse.model_validate(document)


@router.patch("/documents/{document_id}", response_model=KnowledgeDocumentResponse)
async def update_document(
    org_id: uuid.UUID,
    document_id: uuid.UUID,
    body: UpdateKnowledgeDocumentRequest,
    membership: Membership = Depends(require_role(*_KB_MANAGE_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    document = await knowledge_service.get_document(db, org_id, document_id)
    document = await knowledge_service.update_document(db, document, body.title, body.tags, body.review_date)
    return KnowledgeDocumentResponse.model_validate(document)


@router.post("/documents/{document_id}/replace", response_model=KnowledgeDocumentResponse)
async def replace_document(
    org_id: uuid.UUID,
    document_id: uuid.UUID,
    file: UploadFile,
    membership: Membership = Depends(require_role(*_KB_MANAGE_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    document = await knowledge_service.get_document(db, org_id, document_id)
    document = await knowledge_service.replace_document(db, document, membership.user_id, file)
    return KnowledgeDocumentResponse.model_validate(document)


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(
    org_id: uuid.UUID,
    document_id: uuid.UUID,
    membership: Membership = Depends(require_role(*_KB_MANAGE_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    document = await knowledge_service.get_document(db, org_id, document_id)
    await knowledge_service.delete_document(db, document, membership.user_id)
