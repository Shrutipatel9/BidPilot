from io import BytesIO

from pypdf import PdfReader

from app.services.parsers import ParsedQuestion
from app.services.parsers._type_detection import detect_question_type


def parse(content: bytes) -> list[ParsedQuestion]:
    reader = PdfReader(BytesIO(content))
    results: list[ParsedQuestion] = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        for line in text.splitlines():
            line = line.strip()
            if not line.endswith("?"):
                continue

            results.append(
                ParsedQuestion(
                    text=line,
                    position={"kind": "pdf", "page_number": page_number},
                    detected_type=detect_question_type(line),
                    section=None,
                )
            )

    return results
