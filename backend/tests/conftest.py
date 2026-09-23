import os
import subprocess
import sys
from pathlib import Path
from typing import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.db.session import get_db
from app.main import app

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


@pytest_asyncio.fixture(loop_scope="session")
async def client(db_session: AsyncSession) -> AsyncIterator[AsyncClient]:
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
