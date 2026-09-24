import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.answer import Answer, AnswerStatus
from app.models.answer_revision import AnswerRevision
from app.models.question import Question
from app.services.audit_service import log_action

_EDITABLE_STATUSES = (AnswerStatus.ai_drafted, AnswerStatus.needs_review, AnswerStatus.in_review)


async def list_answers(db: AsyncSession, project_id: uuid.UUID) -> list[Answer]:
    result = await db.execute(
        select(Answer).join(Question, Question.id == Answer.question_id).where(Question.project_id == project_id)
    )
    return list(result.scalars().all())


async def _get_answer(db: AsyncSession, project_id: uuid.UUID, answer_id: uuid.UUID) -> Answer:
    result = await db.execute(
        select(Answer)
        .join(Question, Question.id == Answer.question_id)
        .where(Question.project_id == project_id, Answer.id == answer_id)
    )
    answer = result.scalar_one_or_none()
    if answer is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "answer not found")
    return answer


async def update_answer(
    db: AsyncSession, project_id: uuid.UUID, answer_id: uuid.UUID, org_id: uuid.UUID, actor_id: uuid.UUID, text: str
) -> Answer:
    answer = await _get_answer(db, project_id, answer_id)
    answer.text = text
    answer.version += 1
    if answer.status in _EDITABLE_STATUSES:
        answer.status = AnswerStatus.in_review
    db.add(AnswerRevision(answer_id=answer.id, text=text, author="human"))
    await log_action(db, org_id, actor_id, "answer.edited", "answer", str(answer.id))
    await db.commit()
    await db.refresh(answer)
    return answer


async def approve_answer(
    db: AsyncSession, project_id: uuid.UUID, answer_id: uuid.UUID, org_id: uuid.UUID, actor_id: uuid.UUID
) -> Answer:
    answer = await _get_answer(db, project_id, answer_id)
    answer.status = AnswerStatus.approved
    await log_action(db, org_id, actor_id, "answer.approved", "answer", str(answer.id))
    await db.commit()
    await db.refresh(answer)
    return answer


async def reject_answer(
    db: AsyncSession,
    project_id: uuid.UUID,
    answer_id: uuid.UUID,
    org_id: uuid.UUID,
    actor_id: uuid.UUID,
    reason: str,
) -> Answer:
    answer = await _get_answer(db, project_id, answer_id)
    answer.status = AnswerStatus.rejected
    await log_action(db, org_id, actor_id, "answer.rejected", "answer", str(answer.id), details=reason)
    await db.commit()
    await db.refresh(answer)
    return answer
