import re

from app.services.kb_chunking import KbChunk, _MAX_CHARS, _split_by_max_chars

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)


def _chunk_by_headings(text: str) -> list[KbChunk]:
    matches = list(_HEADING_RE.finditer(text))
    chunks: list[KbChunk] = []
    for i, match in enumerate(matches):
        section = match.group(2).strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if not body:
            continue
        for piece in _split_by_max_chars(body):
            chunks.append(KbChunk(text=piece, page=None, section=section))
    return chunks


def _chunk_by_paragraphs(text: str) -> list[KbChunk]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks: list[KbChunk] = []
    current: list[str] = []
    current_len = 0
    for paragraph in paragraphs:
        if current and current_len + len(paragraph) + 2 > _MAX_CHARS:
            chunks.append(KbChunk(text="\n\n".join(current), page=None, section=None))
            current, current_len = [], 0
        current.append(paragraph)
        current_len += len(paragraph) + 2
    if current:
        chunks.append(KbChunk(text="\n\n".join(current), page=None, section=None))
    return chunks


def chunk(content: bytes) -> list[KbChunk]:
    text = content.decode("utf-8", errors="replace")
    if _HEADING_RE.search(text):
        return _chunk_by_headings(text)
    return _chunk_by_paragraphs(text)
