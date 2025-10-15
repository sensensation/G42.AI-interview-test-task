from pydantic import BaseModel, Field


class CsvSkippedRow(BaseModel):
    row_number: int
    reason: str


class CsvNormalizationDTO(BaseModel):
    filename: str
    content: bytes
    content_type: str = "text/csv"
    processed_rows: int
    normalized_rows: int
    skipped_rows: int
    skipped: list[CsvSkippedRow] = Field([], description="Skipped rows for any reason about data set")
