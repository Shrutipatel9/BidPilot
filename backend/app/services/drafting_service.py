import logging
import uuid

from sqlalchemy import select

from app.core.llm_provider import LLMDraftError, generate_draft_answer
from app.db import session as db_session_module
from app.models.answer import Answer, AnswerStatus
from app.models.answer_revision import AnswerRevision
from app.models.organization import Organization
from app.models.question import Question
from app.models.rfp_project import ProjectStatus, RfpProject
from app.services.audit_service import log_action

logger = logging.getLogger("bidpilot.drafting")

_DEFAULT_TONE = "Professional, clear, and factual."


async def run_drafting_for_project(project_id: uuid.UUID, org_id: uuid.UUID, triggered_by_user_id: uuid.UUID) -> None:
    """Entry point handed to FastAPI's BackgroundTasks — must open its own DB session, since
    the request-scoped session from Depends(get_db) is already closed by the time a background
    task runs. Commits per-question, not once at the end, so progress survives a crash/restart
    and the frontend's polling sees incremental status.

    Uses db_session_module.async_session_factory (module attribute lookup, not a name bound at
    import time) so tests/conftest.py can monkeypatch it to reuse the test's own
    transaction-scoped session — a genuinely separate connection wouldn't see data still inside
    that test's uncommitted outer transaction.

    Takes org_id and re-checks it here (not just db.get(RfpProject, project_id)) so the
    isolation guarantee holds by construction rather than depending solely on the calling route
    having already validated it — this function runs fully detached from the HTTP/membership
    context, and shouldn't have to trust every future caller to re-derive that check."""
    async with db_session_module.async_session_factory() as db:
        project = await db.scalar(
            select(RfpProject).where(RfpProject.id == project_id, RfpProject.org_id == org_id)
        )
        if project is None:
            logger.error("drafting requested for missing/mismatched project_id=%s org_id=%s", project_id, org_id)
            return

        org = await db.get(Organization, project.org_id)
        tone = (org.settings or {}).get("tone") or _DEFAULT_TONE

        project.status = ProjectStatus.drafting
        await db.commit()

        result = await db.execute(
            select(Question, Answer)
            .join(Answer, Answer.question_id == Question.id)
            .where(Question.project_id == project_id, Answer.status == AnswerStatus.not_started)
        )
        rows = result.all()

        for question, answer in rows:
            await _draft_one(db, question, answer, tone)

        project.status = ProjectStatus.drafted
        await log_action(db, project.org_id, triggered_by_user_id, "project.drafted", "rfp_project", str(project.id))
        await db.commit()


async def _draft_one(db, question: Question, answer: Answer, tone: str) -> None:
    try:
        draft = await generate_draft_answer(question.text, question.type, None, tone)
    except LLMDraftError:
        logger.exception("drafting failed for question_id=%s", question.id)
        answer.status = AnswerStatus.needs_review
        answer.text = ""
        await db.commit()
        return

    answer.text = draft.answer_text
    answer.choice = draft.choice
    answer.confidence = draft.confidence
    answer.status = AnswerStatus.needs_review if draft.needs_review else AnswerStatus.ai_drafted
    db.add(AnswerRevision(answer_id=answer.id, text=draft.answer_text, author="ai"))
    await db.commit()
