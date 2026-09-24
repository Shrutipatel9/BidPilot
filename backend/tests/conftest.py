import os
import subprocess
import sys
from pathlib import Path
from typing import AsyncIterator
from unittest.mock import Mock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db import session as db_session_module
from app.db.session import get_db
from app.main import app
from app.services import knowledge_service

BACKEND_DIR = Path(__file__).resolve().parents[1]
TEST_DATABASE_URL = settings.test_database_url


@pytest.fixture(scope="session", autouse=True)
def _isolate_email_from_real_smtp():
    """Tests must never depend on a real external SMTP provider (slow, flaky, and sends real
    email) — force the dev-mode fallback (console log + debug_link) for the whole test session
    regardless of the developer's local .env, even when real SMTP credentials are configured
    there for manual testing."""
    original = settings.smtp_host
    settings.smtp_host = None
    yield
    settings.smtp_host = original


@pytest.fixture(scope="session", autouse=True)
def apply_migrations() -> None:
    """Sync, non-async fixture — runs before any pytest-asyncio event loop exists, so
    Alembic's own asyncio.run() (inside alembic/env.py) never collides with one."""
    env = {**os.environ, "DATABASE_URL": TEST_DATABASE_URL}
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_DIR,
        env=env,
        check=True,
    )


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def engine():
    eng = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture(loop_scope="session")
async def db_session(engine) -> AsyncIterator[AsyncSession]:
    async with engine.connect() as connection:
        outer = await connection.begin()
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        yield session
        await session.close()
        await outer.rollback()  # undoes everything the test did, including app-code commit() calls


class _ReuseSessionContextManager:
    """Makes an already-open AsyncSession usable as `async with factory() as db` — used to
    stand in for db_session_module.async_session_factory during tests (see below)."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def __aenter__(self) -> AsyncSession:
        return self._session

    async def __aexit__(self, *exc_info) -> bool:
        return False


@pytest_asyncio.fixture(loop_scope="session")
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    # Background tasks (e.g. drafting_service.run_drafting_for_project) open their own DB
    # session via db_session_module.async_session_factory — a genuinely new connection
    # wouldn't see data still inside this test's uncommitted outer transaction (db_session's
    # SAVEPOINT-based isolation). Patching the factory to hand back this same session, for the
    # duration of the test, keeps background-task code paths testable without weakening that
    # isolation for anything else.
    original_factory = db_session_module.async_session_factory
    db_session_module.async_session_factory = lambda: _ReuseSessionContextManager(db_session)

    # knowledge_service.create_document/replace_document dispatch a real Celery task
    # (ingest_document_task.delay(...)). Celery's own "run it inline for tests" mode
    # (task_always_eager) doesn't work here: the task wrapper calls asyncio.run() internally
    # (see app/workers/ingestion_tasks.py), which raises if invoked from inside a loop that's
    # already running — exactly the situation inside an async test. So tests never dispatch the
    # real task at all; ingestion-pipeline tests instead call
    # ingestion_service.ingest_document(...) directly (an async function, awaitable on the
    # test's own loop, exactly like drafting_service is tested).
    original_delay = knowledge_service.ingest_document_task.delay
    knowledge_service.ingest_document_task.delay = Mock()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    db_session_module.async_session_factory = original_factory
    knowledge_service.ingest_document_task.delay = original_delay
    app.dependency_overrides.clear()
