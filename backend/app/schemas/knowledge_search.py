import uuid

from pydantic import BaseModel


class ChunkSearchResult(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_title: str
    page: int | None
    section: str | None
    snippet: str
    similarity: float
