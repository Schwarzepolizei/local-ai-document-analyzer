import json
import os
from typing import Any

import faiss
import numpy as np


class FaissIndexStore:
    def __init__(self, index_dir: str = "storage/index"):
        self.index_dir = index_dir
        self.index_path = os.path.join(index_dir, "chunks.index")
        self.meta_path = os.path.join(index_dir, "chunks_meta.json")

        os.makedirs(index_dir, exist_ok=True)

    def exists(self) -> bool:
        return os.path.exists(self.index_path) and os.path.exists(self.meta_path)

    def create(self, embeddings: list[list[float]], metadata: list[dict[str, Any]]) -> None:
        if not embeddings:
            raise ValueError("No embeddings to save")

        vectors = np.array(embeddings, dtype="float32")
        dim = vectors.shape[1]

        index = faiss.IndexFlatIP(dim)
        index.add(vectors)

        faiss.write_index(index, self.index_path)

        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)

    def append(self, embeddings: list[list[float]], metadata: list[dict[str, Any]]) -> None:
        if not embeddings:
            raise ValueError("No embeddings to append")

        vectors = np.array(embeddings, dtype="float32")

        if not self.exists():
            self.create(embeddings, metadata)
            return

        index, existing_metadata = self.load()

        if index.d != vectors.shape[1]:
            raise ValueError(
                f"Embedding dimension mismatch: index dim={index.d}, new dim={vectors.shape[1]}"
            )

        index.add(vectors)
        existing_metadata.extend(metadata)

        faiss.write_index(index, self.index_path)

        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(existing_metadata, f, ensure_ascii=False, indent=2)

    def load(self):
        if not os.path.exists(self.index_path):
            raise FileNotFoundError("FAISS index not found")

        if not os.path.exists(self.meta_path):
            raise FileNotFoundError("Metadata file not found")

        index = faiss.read_index(self.index_path)

        with open(self.meta_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)

        return index, metadata

    def clear(self) -> None:
        if os.path.exists(self.index_path):
            os.remove(self.index_path)

        if os.path.exists(self.meta_path):
            os.remove(self.meta_path)

    def list_documents(self) -> list[dict]:
        if not self.exists():
            return []

        _, metadata = self.load()

        grouped = {}

        for item in metadata:
            key = (
                item.get("document_id"),
                item.get("file_name"),
            )

            if key not in grouped:
                grouped[key] = {
                    "document_id": item.get("document_id"),
                    "file_name": item.get("file_name"),
                    "chunks_count": 0,
                }

            grouped[key]["chunks_count"] += 1

        return list(grouped.values())
    
    def overwrite(self, embeddings: list[list[float]], metadata: list[dict[str, Any]]) -> None:
        if not embeddings:
            self.clear()
            return

        vectors = np.array(embeddings, dtype="float32")
        dim = vectors.shape[1]

        index = faiss.IndexFlatIP(dim)
        index.add(vectors)

        faiss.write_index(index, self.index_path)

        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)