import asyncio
import uuid

from app.db import session as db_session_module
from app.services import ingestion_service
from app.workers.celery_app import celery_app


async def _run(document_id: str) -> None:
    try:
        await ingestion_service.ingest_document(uuid.UUID(document_id))
    finally:
        # Each task invocation gets its own asyncio.run() event loop, but the shared engine's
        # pooled asyncpg connections are bound to whichever loop created them and break once
        # that loop closes (surfaced as "Event loop is closed" on the *next* task otherwise).
        # Disposing here forces the pool to reconnect fresh under the next task's loop instead
        # of reusing a connection tied to one that's gone. A no-op in tests, where this engine
        # is never actually used (async_session_factory is monkeypatched to the test's own
        # session instead).
        await db_session_module.engine.dispose()


@celery_app.task
def ingest_document_task(document_id: str) -> None:
    """Thin wrapper — the real logic lives in ingestion_service.ingest_document, which is
    directly unit-testable without going through Celery at all."""
    asyncio.run(_run(document_id))
