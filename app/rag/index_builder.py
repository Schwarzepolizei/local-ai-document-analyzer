from app.rag.embedder import EmbeddingService
from app.rag.index_store import FaissIndexStore


class IndexBuilder:
    def __init__(self):
        self.embedder = EmbeddingService()
        self.store = FaissIndexStore()

    def build_from_etl_response(self, etl_response: dict) -> dict:
        chunks = etl_response.get("content", {}).get("chunks", [])
        document_id = etl_response.get("document_id")
        file_name = etl_response.get("source", {}).get("file_name")

        if not chunks:
            raise ValueError("No chunks found in ETL response")

        texts = [chunk["text"] for chunk in chunks]

        metadata = []
        for chunk in chunks:
            metadata.append(
                {
                    "document_id": document_id,
                    "file_name": file_name,
                    "chunk_id": chunk.get("chunk_id"),
                    "chunk_order": chunk.get("chunk_order"),
                    "text": chunk.get("text"),
                    "page_span": chunk.get("page_span", []),
                    "block_types": chunk.get("block_types", []),
                    "char_count": chunk.get("char_count", 0),

                    "section_title": chunk.get("section_title"),
                    "content_type": chunk.get("content_type", "text"),
                    "source_context": chunk.get("source_context"),
                    "token_estimate": chunk.get("token_estimate", 0),
                }
            )

        embeddings = self.embedder.embed_texts(texts)
        self.store.append(embeddings, metadata)

        return {
            "status": "success",
            "indexed_chunks": len(chunks),
            "document_id": document_id,
            "file_name": file_name,
        }