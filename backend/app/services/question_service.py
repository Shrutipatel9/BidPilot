import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.storage import download_bytes
from app.models.answer import Answer
from app.models.question import Question
from app.models.rfp_project import ProjectStatus, RfpProject
from app.services.audit_service import log_action
from app.services.parsers import parse_file


async def parse_and_stage_questions(
    db: AsyncSession, project: RfpProject, actor_id: uuid.UUID
) -> list[Question]:
    content = await download_bytes(project.source_file_key)
    parsed = parse_file(content, project.source_file_ext)

    questions = [
        Question(
            project_id=project.id,
            text=p.text,
            section=p.section,
            type=p.detected_type,
            position=p.position,
        )
        for p in parsed
    ]
    db.add_all(questions)
    await log_action(db, project.org_id, actor_id, "project.parsed", "rfp_project", str(project.id))
    await db.commit()
    for q in questions:
        await db.refresh(q)
    return questions


async def list_questions(db: AsyncSession, project_id: uuid.UUID) -> list[Question]:
    result = await db.execute(
        select(Question).where(Question.project_id == project_id).order_by(Question.created_at)
    )
    return list(result.scalars().all())


async def _get_question(db: AsyncSession, project_id: uuid.UUID, question_id: uuid.UUID) -> Question:
    result = await db.execute(
        select(Question).where(Question.project_id == project_id, Question.id == question_id)
    )
    question = result.scalar_one_or_none()
    if question is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "question not found")
    return question


async def update_question(
    db: AsyncSession,
    project_id: uuid.UUID,
    question_id: uuid.UUID,
    text: str | None,
    section: str | None,
    type_: str | None,
) -> Question:
    question = await _get_question(db, project_id, question_id)
    if text is not None:
        question.text = text
    if section is not None:
        question.section = section
    if type_ is not None:
        question.type = type_
    await db.commit()
    await db.refresh(question)
    return question


async def confirm_questions(db: AsyncSession, project: RfpProject, actor_id: uuid.UUID) -> RfpProject:
    questions = await list_questions(db, project.id)
    if not questions:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "no questions to confirm — parse the questionnaire first")

    for question in questions:
        existing = await db.scalar(select(Answer).where(Answer.question_id == question.id))
        if existing is None:
            db.add(Answer(question_id=question.id))

    project.status = ProjectStatus.questions_confirmed
    await log_action(db, project.org_id, actor_id, "project.questions_confirmed", "rfp_project", str(project.id))
    await db.commit()
    await db.refresh(project)
    return project
