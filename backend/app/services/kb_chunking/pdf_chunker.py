from io import BytesIO

from pypdf import PdfReader

from app.services.kb_chunking import KbChunk, _split_by_max_chars


def chunk(content: bytes) -> list[KbChunk]:
    reader = PdfReader(BytesIO(content))
    chunks: list[KbChunk] = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if not text:
            continue
        for piece in _split_by_max_chars(text):
            chunks.append(KbChunk(text=piece, page=page_number, section=None))

    return chunks
