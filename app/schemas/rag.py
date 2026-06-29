from pydantic import BaseModel
from typing import Optional


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5
    document_id: Optional[str] = None
    file_name: Optional[str] = None


class IndexResponse(BaseModel):
    status: str
    indexed_chunks: int
    document_id: str | None = None
    file_name: str | None = None


class SearchResult(BaseModel):
    document_id: str | None = None
    file_name: str | None = None
    chunk_id: str | None = None
    chunk_order: int | None = None
    text: str
    page_span: list[int] = []
    block_types: list[str] = []
    char_count: int = 0
    score: float
    section_title: str | None = None
    content_type: str = "text"
    source_context: str | None = None
    token_estimate: int = 0


class SearchResponse(BaseModel):
    query: str
    top_k: int
    results: list[SearchResult]


class AskRequest(BaseModel):
    query: str
    top_k: int = 5
    document_id: Optional[str] = None
    file_name: Optional[str] = None


class AskResponse(BaseModel):
    query: str
    answer: str
    context: str
    results: list[SearchResult]


class IndexedDocumentInfo(BaseModel):
    document_id: str | None = None
    file_name: str | None = None
    chunks_count: int


class DocumentsResponse(BaseModel):
    documents: list[IndexedDocumentInfo]


class DeleteDocumentRequest(BaseModel):
    document_id: str | None = None
    file_name: str | None = None


class DeleteDocumentResponse(BaseModel):
    status: str
    removed_chunks: int
    remaining_chunks: int