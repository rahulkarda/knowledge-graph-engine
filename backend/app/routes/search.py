from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.node import KnowledgeNode
from app.schemas.search import SemanticSearchRequest, SemanticSearchResponse, SearchResult
from app.services.qa_service import _score

router = APIRouter()


@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(
    payload: SemanticSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    results = []

    # Try vector-based semantic search first
    try:
        from app.services.vector_store import VectorStore
        from app.services.embedding_service import EmbeddingService

        embedding_service = EmbeddingService()
        vector_store = VectorStore()

        query_embedding = embedding_service.embed_text(payload.query)
        hits = vector_store.search(query_embedding, top_k=payload.top_k, content_type=payload.content_type)

        for hit in hits:
            node_id = hit["node_id"]
            score = hit["score"]
            excerpt = hit["text"][:300]

            stmt = select(KnowledgeNode).where(KnowledgeNode.id == node_id)
            res = await db.execute(stmt)
            node = res.scalar_one_or_none()
            if node:
                results.append(SearchResult(
                    node_id=node_id,
                    title=node.title,
                    content_type=node.content_type,
                    excerpt=excerpt,
                    score=score,
                    created_at=node.created_at.isoformat(),
                ))

        if results:
            return SemanticSearchResponse(query=payload.query, results=results, total=len(results))

    except Exception:
        pass

    # Fallback: TF-style scored search with proper ranking
    stmt = select(KnowledgeNode).order_by(KnowledgeNode.created_at.desc()).limit(500)
    if payload.content_type:
        stmt = stmt.where(KnowledgeNode.content_type == payload.content_type)

    res = await db.execute(stmt)
    nodes = res.scalars().all()

    scored = []
    for node in nodes:
        s = _score(payload.query, node.title, node.content)
        if s > 0:
            scored.append((s, node))

    scored.sort(key=lambda x: x[0], reverse=True)

    for score, node in scored[: payload.top_k]:
        results.append(SearchResult(
            node_id=node.id,
            title=node.title,
            content_type=node.content_type,
            excerpt=node.content[:300],
            score=score,
            created_at=node.created_at.isoformat(),
        ))

    return SemanticSearchResponse(query=payload.query, results=results, total=len(results))


@router.get("/keyword")
async def keyword_search(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(KnowledgeNode)
        .where(KnowledgeNode.content.ilike(f"%{q}%") | KnowledgeNode.title.ilike(f"%{q}%"))
        .limit(limit)
        .order_by(KnowledgeNode.created_at.desc())
    )
    result = await db.execute(stmt)
    nodes = result.scalars().all()
    return [
        {
            "node_id": n.id,
            "title": n.title,
            "content_type": n.content_type,
            "excerpt": n.content[:300],
            "created_at": n.created_at.isoformat(),
        }
        for n in nodes
    ]
