import json
import uuid
from datetime import date

from fastapi import APIRouter, Depends, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import get_membership, require_role
from app.db.session import get_db
from app.models.membership import Membership, MembershipRole
from app.schemas.project import ProjectResponse
from app.services import project_service

router = APIRouter(prefix="/api/orgs/{org_id}/projects", tags=["projects"])


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    org_id: uuid.UUID,
    file: UploadFile,
    name: str = Form(...),
    buyer: str | None = Form(None),
    due_date: date | None = Form(None),
    tags: str = Form("[]"),
    membership: Membership = Depends(require_role(MembershipRole.owner, MembershipRole.admin, MembershipRole.responder)),
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.create_project(
        db, org_id, membership.user_id, name, buyer, due_date, json.loads(tags), file
    )
    return ProjectResponse.model_validate(project)


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    org_id: uuid.UUID,
    membership: Membership = Depends(get_membership),
    db: AsyncSession = Depends(get_db),
):
    projects = await project_service.list_projects(db, org_id)
    return [ProjectResponse.model_validate(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    membership: Membership = Depends(get_membership),
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, org_id, project_id)
    return ProjectResponse.model_validate(project)
