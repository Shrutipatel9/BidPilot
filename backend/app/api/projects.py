import json
import uuid
from datetime import date

from fastapi import APIRouter, BackgroundTasks, Depends, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import get_membership, require_role
from app.db.session import get_db
from app.models.membership import Membership, MembershipRole
from app.schemas.answer import AnswerResponse, RejectAnswerRequest, UpdateAnswerRequest
from app.schemas.project import ProjectResponse
from app.schemas.question import QuestionResponse, UpdateQuestionRequest
from app.services import answer_service, project_service, question_service
from app.services.drafting_service import run_drafting_for_project

router = APIRouter(prefix="/api/orgs/{org_id}/projects", tags=["projects"])

_EDITOR_ROLES = (MembershipRole.owner, MembershipRole.admin, MembershipRole.responder)
_REVIEW_ROLES = (*_EDITOR_ROLES, MembershipRole.reviewer)


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    org_id: uuid.UUID,
    file: UploadFile,
    name: str = Form(...),
    buyer: str | None = Form(None),
    due_date: date | None = Form(None),
    tags: str = Form("[]"),
    membership: Membership = Depends(require_role(*_EDITOR_ROLES)),
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


@router.post("/{project_id}/parse", response_model=list[QuestionResponse])
async def parse_project(
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    membership: Membership = Depends(require_role(*_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, org_id, project_id)
    questions = await question_service.parse_and_stage_questions(db, project, membership.user_id)
    return [QuestionResponse.model_validate(q) for q in questions]


@router.get("/{project_id}/questions", response_model=list[QuestionResponse])
async def list_questions(
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    membership: Membership = Depends(get_membership),
    db: AsyncSession = Depends(get_db),
):
    await project_service.get_project(db, org_id, project_id)  # 404s / tenant-scopes the project_id
    questions = await question_service.list_questions(db, project_id)
    return [QuestionResponse.model_validate(q) for q in questions]


@router.patch("/{project_id}/questions/{question_id}", response_model=QuestionResponse)
async def update_question(
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    question_id: uuid.UUID,
    body: UpdateQuestionRequest,
    membership: Membership = Depends(require_role(*_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    await project_service.get_project(db, org_id, project_id)
    question = await question_service.update_question(
        db, project_id, question_id, body.text, body.section, body.type
    )
    return QuestionResponse.model_validate(question)


@router.post("/{project_id}/questions/confirm", response_model=ProjectResponse)
async def confirm_questions(
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    membership: Membership = Depends(require_role(*_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    project = await project_service.get_project(db, org_id, project_id)
    project = await question_service.confirm_questions(db, project, membership.user_id)
    return ProjectResponse.model_validate(project)


@router.post("/{project_id}/draft", status_code=202)
async def start_drafting(
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    membership: Membership = Depends(require_role(*_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    await project_service.get_project(db, org_id, project_id)  # 404s / tenant-scopes the project_id
    background_tasks.add_task(run_drafting_for_project, project_id, org_id, membership.user_id)
    return {"status": "queued"}


@router.get("/{project_id}/answers", response_model=list[AnswerResponse])
async def list_answers(
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    membership: Membership = Depends(get_membership),
    db: AsyncSession = Depends(get_db),
):
    await project_service.get_project(db, org_id, project_id)
    answers = await answer_service.list_answers(db, project_id)
    return [AnswerResponse.model_validate(a) for a in answers]


@router.patch("/{project_id}/answers/{answer_id}", response_model=AnswerResponse)
async def update_answer(
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    answer_id: uuid.UUID,
    body: UpdateAnswerRequest,
    membership: Membership = Depends(require_role(*_EDITOR_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    await project_service.get_project(db, org_id, project_id)
    answer = await answer_service.update_answer(db, project_id, answer_id, org_id, membership.user_id, body.text)
    return AnswerResponse.model_validate(answer)


@router.post("/{project_id}/answers/{answer_id}/approve", response_model=AnswerResponse)
async def approve_answer(
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    answer_id: uuid.UUID,
    membership: Membership = Depends(require_role(*_REVIEW_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    await project_service.get_project(db, org_id, project_id)
    answer = await answer_service.approve_answer(db, project_id, answer_id, org_id, membership.user_id)
    return AnswerResponse.model_validate(answer)


@router.post("/{project_id}/answers/{answer_id}/reject", response_model=AnswerResponse)
async def reject_answer(
    org_id: uuid.UUID,
    project_id: uuid.UUID,
    answer_id: uuid.UUID,
    body: RejectAnswerRequest,
    membership: Membership = Depends(require_role(*_REVIEW_ROLES)),
    db: AsyncSession = Depends(get_db),
):
    await project_service.get_project(db, org_id, project_id)
    answer = await answer_service.reject_answer(db, project_id, answer_id, org_id, membership.user_id, body.reason)
    return AnswerResponse.model_validate(answer)
