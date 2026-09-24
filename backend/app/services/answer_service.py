import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.answer import Answer
from app.models.question import Question


async def list_answers(db: AsyncSession, project_id: uuid.UUID) -> list[Answer]:
    result = await db.execute(
        select(Answer).join(Question, Question.id == Answer.question_id).where(Question.project_id == project_id)
    )
    return list(result.scalars().all())
