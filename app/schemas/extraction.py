from pydantic import BaseModel


class ExtractedItem(BaseModel):
    field: str
    value: str
    source: str | None = None
    confidence: str | None = None


class ExtractionResult(BaseModel):
    document_id: str
    file_name: str
    request: str
    items: list[ExtractedItem] = []
    missing: list[str] = []
    notes: list[str] = []
