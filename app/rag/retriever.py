from typing import Any, Optional

import numpy as np

from app.rag.embedder import EmbeddingService
from app.rag.index_store import FaissIndexStore


class Retriever:
    def __init__(self):
        self.embedder = EmbeddingService()
        self.store = FaissIndexStore()

    def search(
        self,
        query: str,
        top_k: int = 5,
        document_id: Optional[str] = None,
        file_name: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        index, metadata = self.store.load()

        query_vector = np.array([self.embedder.embed_query(query)], dtype="float32")

        candidate_k = min(max(top_k * 5, 20), len(metadata))
        scores, indices = index.search(query_vector, candidate_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(metadata):
                continue

            item = metadata[idx].copy()

            if document_id is not None and item.get("document_id") != document_id:
                continue

            if file_name is not None and item.get("file_name") != file_name:
                continue

            item["score"] = float(score)
            results.append(item)

            if len(results) >= top_k:
                break

        return results