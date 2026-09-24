from dataclasses import dataclass


@dataclass
class KbChunk:
    text: str
    page: int | None
    section: str | None


_MAX_CHARS = 2000


def _split_by_max_chars(text: str, max_chars: int = _MAX_CHARS) -> list[str]:
    """Greedily packs whitespace-separated words into pieces up to max_chars, so an overlong
    section still splits on a word boundary rather than mid-word. Returns [text] unchanged if
    it already fits."""
    words = text.split()
    if not words:
        return []
    pieces: list[str] = []
    current: list[str] = []
    current_len = 0
    for word in words:
        added_len = len(word) + (1 if current else 0)
        if current and current_len + added_len > max_chars:
            pieces.append(" ".join(current))
            current, current_len = [], 0
            added_len = len(word)
        current.append(word)
        current_len += added_len
    if current:
        pieces.append(" ".join(current))
    return pieces


# Imported after KbChunk/_MAX_CHARS are defined above, since each chunker module imports them
# at module level — mirrors app/services/parsers/__init__.py's ordering to avoid a circular
# import without function-local imports.
from app.services.kb_chunking import docx_chunker, pdf_chunker, text_chunker, xlsx_chunker  # noqa: E402


def chunk_file(content: bytes, ext: str) -> list[KbChunk]:
    if ext == "docx":
        return docx_chunker.chunk(content)
    if ext == "pdf":
        return pdf_chunker.chunk(content)
    if ext == "xlsx":
        return xlsx_chunker.chunk(content)
    if ext in ("txt", "md"):
        return text_chunker.chunk(content)
    raise ValueError(f"no chunker available for '.{ext}'")
