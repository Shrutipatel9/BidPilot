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
from app.services.retrieval_service import RetrievedChunk, retrieve_top_chunks

logger = logging.getLogger("bidpilot.drafting")

_DEFAULT_TONE = "Professional, clear, and factual."
_INSUFFICIENT_INFO = "Insufficient information"
_TOP_K = 5


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
            await _draft_one(db, question, answer, tone, project.org_id)

        project.status = ProjectStatus.drafted
        await log_action(db, project.org_id, triggered_by_user_id, "project.drafted", "rfp_project", str(project.id))
        await db.commit()


def _citations_for(chunks: list[RetrievedChunk]) -> list[dict]:
    return [
        {
            "chunk_id": str(c.chunk_id),
            "document_id": str(c.document_id),
            "document_title": c.document_title,
            "page": c.page,
            "section": c.section,
            "snippet": c.text[:200],
        }
        for c in chunks
    ]


async def _draft_one(db, question: Question, answer: Answer, tone: str, org_id: uuid.UUID) -> None:
    chunks = await retrieve_top_chunks(db, org_id, question.text, top_k=_TOP_K)

    if not chunks:
        # No knowledge base evidence at all — this needs no LLM judgment call (see
        # drafting_service module docs / Phase 2 plan): there is nothing to ground an answer in.
        answer.text = _INSUFFICIENT_INFO
        answer.choice = None
        answer.confidence = 0
        answer.status = AnswerStatus.needs_review
        answer.citations = []
        db.add(AnswerRevision(answer_id=answer.id, text=_INSUFFICIENT_INFO, author="ai"))
        await db.commit()
        return

    try:
        draft = await generate_draft_answer(question.text, question.type, None, tone, chunks)
    except LLMDraftError:
        logger.exception("drafting failed for question_id=%s", question.id)
        answer.status = AnswerStatus.needs_review
        answer.text = ""
        answer.citations = []
        await db.commit()
        return

    # Confidence is retrieval-grounded, not just the LLM's raw self-assessment: a confidently
    # worded answer over weak evidence still shows a low score, since it's capped by how well
    # the top retrieved chunk actually matched the question.
    retrieval_confidence = round(max(0.0, min(1.0, chunks[0].similarity)) * 100)
    is_insufficient = draft.answer_text.strip() == _INSUFFICIENT_INFO

    answer.text = draft.answer_text
    answer.choice = draft.choice
    answer.confidence = min(draft.confidence, retrieval_confidence)
    answer.status = AnswerStatus.needs_review if (draft.needs_review or is_insufficient) else AnswerStatus.ai_drafted
    # No claim is being made when the model says it doesn't know — nothing to cite.
    answer.citations = [] if is_insufficient else _citations_for(chunks)
    db.add(AnswerRevision(answer_id=answer.id, text=draft.answer_text, author="ai"))
    await db.commit()
