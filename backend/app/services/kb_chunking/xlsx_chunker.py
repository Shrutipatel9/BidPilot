from io import BytesIO

import openpyxl

from app.services.kb_chunking import KbChunk, _MAX_CHARS


def chunk(content: bytes) -> list[KbChunk]:
    wb = openpyxl.load_workbook(BytesIO(content), data_only=True)
    chunks: list[KbChunk] = []

    for ws in wb.worksheets:
        row_lines = []
        for row in ws.iter_rows():
            cells = [str(cell.value).strip() for cell in row if cell.value is not None and str(cell.value).strip()]
            if cells:
                row_lines.append(" | ".join(cells))
        if not row_lines:
            continue

        # Row-grouped, capped at _MAX_CHARS — a small sheet naturally lands in one chunk.
        current: list[str] = []
        current_len = 0
        for line in row_lines:
            if current and current_len + len(line) + 1 > _MAX_CHARS:
                chunks.append(KbChunk(text="\n".join(current), page=None, section=ws.title))
                current, current_len = [], 0
            current.append(line)
            current_len += len(line) + 1
        if current:
            chunks.append(KbChunk(text="\n".join(current), page=None, section=ws.title))

    return chunks
