from dataclasses import dataclass

from fastapi import HTTPException, status


@dataclass
class ParsedQuestion:
    text: str
    position: dict
    detected_type: str
    section: str | None


# Imported after ParsedQuestion is defined above, since each parser module imports it at
# module level — reordering this way avoids a circular import without resorting to
# function-local imports in the parser modules.
from app.services.parsers import docx_parser, pdf_parser, xlsx_parser  # noqa: E402


def parse_file(content: bytes, ext: str) -> list[ParsedQuestion]:
    if ext == "xlsx":
        return xlsx_parser.parse(content)
    if ext == "docx":
        return docx_parser.parse(content)
    if ext == "pdf":
        return pdf_parser.parse(content)
    raise HTTPException(status.HTTP_400_BAD_REQUEST, f"no parser available for '.{ext}'")
