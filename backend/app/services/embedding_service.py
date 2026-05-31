from typing import List


class EmbeddingService:
    def __init__(self):
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            from app.config import settings
            self._model = SentenceTransformer(settings.embedding_model)
        return self._model

    def embed_text(self, text: str) -> List[float]:
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(texts, convert_to_numpy=True, batch_size=32)
        return [e.tolist() for e in embeddings]
