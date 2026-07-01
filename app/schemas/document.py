from pydantic import BaseModel


class BBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float


class Block(BaseModel):
    block_id: str
    page_num: int
    block_order: int
    block_type: str
    text: str
    bbox: BBox | None = None
    confidence: float | None = None


class Chunk(BaseModel):
    chunk_id: str
    chunk_order: int
    block_ids: list[str]
    text: str

    page_span: list[int] = []
    block_types: list[str] = []
    char_count: int = 0

    section_title: str | None = None
    content_type: str = "text"
    source_context: str | None = None
    token_estimate: int = 0


class Page(BaseModel):
    page_num: int
    text: str
    width: int | None = None
    height: int | None = None
    confidence: float | None = None
    quality_score: float | None = None


class DocumentMeta(BaseModel):
    language: list[str]
    page_count: int | None = None
    is_scanned: bool
    extraction_method: str
    text_extracted: bool
    quality_score: float | None = None
    quality_label: str | None = None


class SourceMeta(BaseModel):
    file_name: str
    file_type: str


class ProcessingStats(BaseModel):
    pages_count: int = 0
    blocks_count: int = 0
    chunks_count: int = 0
    empty_pages_count: int = 0
    text_length: int = 0
    avg_page_confidence: float | None = None
    avg_page_quality: float | None = None

    tables_count: int = 0
    table_rows_count: int = 0
    images_count: int = 0
    equations_count: int = 0
    embedded_objects_count: int = 0


class ProcessingInfo(BaseModel):
    status: str
    pipeline_version: str
    duration_ms: int | None = None
    warnings: list[str] = []
    errors: list[str] = []
    stats: ProcessingStats | None = None


class Content(BaseModel):
    full_text: str
    pages: list[Page]
    blocks: list[Block]
    chunks: list[Chunk]


class ETLResponse(BaseModel):
    document_id: str
    source: SourceMeta
    document: DocumentMeta
    content: Content
    processing: ProcessingInfo
