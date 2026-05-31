from typing import List, Dict, Optional
from app.config import settings


class VectorStore:
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from qdrant_client import QdrantClient
            if settings.qdrant_api_key:
                self._client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
            else:
                self._client = QdrantClient(url=settings.qdrant_url)
            self._ensure_collection()
        return self._client

    def _ensure_collection(self):
        from qdrant_client.models import Distance, VectorParams
        existing = [c.name for c in self._client.get_collections().collections]
        if settings.qdrant_collection not in existing:
            self._client.create_collection(
                collection_name=settings.qdrant_collection,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )

    def upsert(self, node_id: str, chunks: List[str], embeddings: List[List[float]], metadata: Dict):
        from qdrant_client.models import PointStruct

        points = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            point_id = abs(hash(f"{node_id}_{i}")) % (2**63)
            points.append(PointStruct(
                id=point_id,
                vector=emb,
                payload={
                    "node_id": node_id,
                    "chunk_index": i,
                    "text": chunk,
                    **metadata,
                },
            ))

        self.client.upsert(collection_name=settings.qdrant_collection, points=points)

    def search(
        self, query_embedding: List[float], top_k: int = 10, content_type: Optional[str] = None
    ) -> List[Dict]:
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        query_filter = None
        if content_type:
            query_filter = Filter(
                must=[FieldCondition(key="content_type", match=MatchValue(value=content_type))]
            )

        results = self.client.search(
            collection_name=settings.qdrant_collection,
            query_vector=query_embedding,
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        )

        seen_nodes = set()
        hits = []
        for r in results:
            node_id = r.payload.get("node_id")
            if node_id and node_id not in seen_nodes:
                seen_nodes.add(node_id)
                hits.append({
                    "node_id": node_id,
                    "score": r.score,
                    "text": r.payload.get("text", ""),
                })

        return hits

    def delete_node(self, node_id: str):
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        self.client.delete(
            collection_name=settings.qdrant_collection,
            points_selector=Filter(
                must=[FieldCondition(key="node_id", match=MatchValue(value=node_id))]
            ),
        )
