# Every model must be imported here so SQLAlchemy's declarative registry can resolve
# cross-table foreign keys/relationships regardless of which entrypoint imports `app.models`
# first. The FastAPI app happens to import all of these transitively through its routers, but
# a Celery worker process only imports what its own tasks need (e.g. KnowledgeChunk/
# KnowledgeDocument) — without this, resolving `knowledge_chunks.org_id`'s FK to
# `organizations` fails with NoReferencedTableError the first time the worker touches the DB,
# since the Organization model was never imported anywhere in that process.
from app.models import (  # noqa: F401
    answer,
    answer_revision,
    audit_log,
    invitation,
    knowledge_chunk,
    knowledge_document,
    membership,
    organization,
    question,
    refresh_token,
    rfp_project,
    user,
)
