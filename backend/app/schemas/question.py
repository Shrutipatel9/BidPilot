import uuid
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class XlsxPosition(BaseModel):
    kind: Literal["xlsx"] = "xlsx"
    sheet_name: str
    question_row: int
    question_col: int
    answer_row: int
    answer_col: int


class DocxPosition(BaseModel):
    kind: Literal["docx"] = "docx"
    anchor: Literal["paragraph", "table_cell"]
    paragraph_index: int | None = None
    table_index: int | None = None
    row_index: int | None = None
    col_index: int | None = None
    has_placeholder: bool
    question_fingerprint: str


class PdfPosition(BaseModel):
    kind: Literal["pdf"] = "pdf"
    page_number: int


Position = Annotated[Union[XlsxPosition, DocxPosition, PdfPosition], Field(discriminator="kind")]


class QuestionResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    text: str
    section: str | None
    type: str
    category: str | None
    position: XlsxPosition | DocxPosition | PdfPosition
    duplicate_of: uuid.UUID | None

    model_config = {"from_attributes": True}


class UpdateQuestionRequest(BaseModel):
    text: str | None = None
    section: str | None = None
    type: str | None = None
