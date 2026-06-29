from app.rag.embedder import EmbeddingService
from app.rag.index_store import FaissIndexStore


class DocumentManager:
    def __init__(self):
        self.store = FaissIndexStore()
        self.embedder = EmbeddingService()

    def delete_document(
        self,
        document_id: str | None = None,
        file_name: str | None = None,
    ) -> dict:
        if document_id is None and file_name is None:
            raise ValueError("Either document_id or file_name must be provided")

        if not self.store.exists():
            return {
                "status": "success",
                "removed_chunks": 0,
                "remaining_chunks": 0,
            }

        _, metadata = self.store.load()

        kept_metadata = []
        removed_metadata = []

        for item in metadata:
            matches = True

            if document_id is not None:
                matches = matches and item.get("document_id") == document_id

            if file_name is not None:
                matches = matches and item.get("file_name") == file_name

            if matches:
                removed_metadata.append(item)
            else:
                kept_metadata.append(item)

        removed_chunks = len(removed_metadata)
        remaining_chunks = len(kept_metadata)

        if not kept_metadata:
            self.store.clear()
            return {
                "status": "success",
                "removed_chunks": removed_chunks,
                "remaining_chunks": 0,
            }

        texts = [item["text"] for item in kept_metadata]
        embeddings = self.embedder.embed_texts(texts)

        self.store.overwrite(embeddings, kept_metadata)

        return {
            "status": "success",
            "removed_chunks": removed_chunks,
            "remaining_chunks": remaining_chunks,
        }