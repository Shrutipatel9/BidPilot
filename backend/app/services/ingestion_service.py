import logging
import uuid

from app.core.embedding_provider import EmbeddingError, generate_embedding
from app.core.storage import download_bytes
from app.db import session as db_session_module
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_document import DocumentStatus, KnowledgeDocument
from app.services.kb_chunking import chunk_file

logger = logging.getLogger("bidpilot.ingestion")


async def ingest_document(document_id: uuid.UUID) -> None:
    """Entry point handed to the Celery ingestion task — must open its own DB session, same
    reasoning as drafting_service.run_drafting_for_project (runs detached from any request's
    session lifecycle). Uses db_session_module.async_session_factory (module attribute lookup)
    so tests can monkeypatch it to reuse the test's own transaction, exactly like drafting."""
    async with db_session_module.async_session_factory() as db:
        document = await db.get(KnowledgeDocument, document_id)
        if document is None:
            logger.error("ingestion requested for missing document_id=%s", document_id)
            return

        # A fresh upload starts at "uploaded", not "processing" — set it explicitly here so
        # the frontend's poll-while-processing check has something to actually observe (a
        # replace() call already sets this before dispatching, but a first-time create() never
        # did, so without this the status silently jumped straight from "uploaded" to its final
        # state and the UI never picked up the completion).
        document.status = DocumentStatus.processing
        await db.commit()

        try:
            content = await download_bytes(document.source_file_key)
            chunks = chunk_file(content, document.source_file_ext)
        except Exception:
            logger.exception("chunking failed for document_id=%s", document_id)
            document.status = DocumentStatus.failed
            await db.commit()
            return

        failed_count = 0
        for kb_chunk in chunks:
            try:
                embedding = await generate_embedding(kb_chunk.text)
            except EmbeddingError:
                logger.exception("embedding failed for one chunk of document_id=%s", document_id)
                failed_count += 1
                continue
            db.add(
                KnowledgeChunk(
                    document_id=document.id,
                    org_id=document.org_id,
                    text=kb_chunk.text,
                    page=kb_chunk.page,
                    section=kb_chunk.section,
                    embedding=embedding,
                )
            )
            await db.commit()

        # A document with zero indexable chunks (either no chunks at all, or every embedding
        # call failed) isn't usable for retrieval — flag it rather than silently marking
        # "indexed" with nothing to actually retrieve. Partial success still counts as indexed,
        # matching the per-question failure isolation precedent in drafting_service.
        document.status = DocumentStatus.failed if failed_count == len(chunks) or not chunks else DocumentStatus.indexed
        if failed_count:
            logger.warning(
                "document_id=%s indexed with %d/%d chunks failing to embed", document_id, failed_count, len(chunks)
            )
        await db.commit()
