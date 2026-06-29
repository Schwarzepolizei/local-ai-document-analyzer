from sentence_transformers import SentenceTransformer

_model = None


def get_model():
    global _model
    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        print("Embedding model loaded")
    return _model


class EmbeddingService:
    def __init__(self):
        self.model = get_model()

    def embed_texts(self, texts: list[str]):
        return self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).tolist()

    def embed_query(self, text: str):
        return self.model.encode(
            [text],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )[0].tolist()