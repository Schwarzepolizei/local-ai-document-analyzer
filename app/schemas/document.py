from pydantic import BaseModel
from typing import List, Optional, Dict, Any


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
    bbox: Optional[BBox] = None
    confidence: Optional[float] = None


class Chunk(BaseModel):
    chunk_id: str
    chunk_order: int
    block_ids: List[str]
    text: str

    page_span: List[int] = []
    block_types: List[str] = []
    char_count: int = 0

    section_title: Optional[str] = None
    content_type: str = "text"
    source_context: Optional[str] = None
    token_estimate: int = 0


class Page(BaseModel):
    page_num: int
    text: str
    width: Optional[int] = None
    height: Optional[int] = None
    confidence: Optional[float] = None
    quality_score: Optional[float] = None


class DocumentMeta(BaseModel):
    language: List[str]
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
    avg_page_confidence: Optional[float] = None
    avg_page_quality: Optional[float] = None

    tables_count: int = 0
    table_rows_count: int = 0
    images_count: int = 0
    equations_count: int = 0
    embedded_objects_count: int = 0


class ProcessingInfo(BaseModel):
    status: str
    pipeline_version: str
    duration_ms: Optional[int] = None
    warnings: List[str] = []
    errors: List[str] = []
    stats: Optional[ProcessingStats] = None


class Content(BaseModel):
    full_text: str
    pages: List[Page]
    blocks: List[Block]
    chunks: List[Chunk]


class ETLResponse(BaseModel):
    document_id: str
    source: SourceMeta
    document: DocumentMeta
    content: Content
    processing: ProcessingInfo