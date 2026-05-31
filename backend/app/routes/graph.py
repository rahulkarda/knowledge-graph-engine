from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.node import KnowledgeNode
from app.models.edge import KnowledgeEdge
from app.schemas.edge import EdgeCreate, EdgeOut

router = APIRouter()


@router.get("/full")
async def get_full_graph(db: AsyncSession = Depends(get_db)):
    nodes_res = await db.execute(select(KnowledgeNode).order_by(KnowledgeNode.created_at.desc()))
    all_nodes = nodes_res.scalars().all()

    edges_res = await db.execute(select(KnowledgeEdge))
    all_edges = edges_res.scalars().all()

    return {
        "nodes": [
            {
                "id": n.id,
                "title": n.title,
                "content_type": n.content_type,
                "created_at": n.created_at.isoformat(),
                "word_count": n.word_count,
            }
            for n in all_nodes
        ],
        "links": [
            {
                "id": e.id,
                "source": e.source_node_id,
                "target": e.target_node_id,
                "relationship": e.rel_type,
                "weight": e.weight,
                "edge_type": e.edge_type,
            }
            for e in all_edges
        ],
    }


@router.get("/subgraph/{node_id}")
async def get_subgraph(node_id: str, hops: int = 2, db: AsyncSession = Depends(get_db)):
    visited = set()
    frontier = {node_id}
    all_node_ids = {node_id}

    for _ in range(hops):
        if not frontier:
            break
        edge_stmt = select(KnowledgeEdge).where(
            KnowledgeEdge.source_node_id.in_(frontier) | KnowledgeEdge.target_node_id.in_(frontier)
        )
        edges_res = await db.execute(edge_stmt)
        hop_edges = edges_res.scalars().all()
        new_frontier = set()
        for e in hop_edges:
            all_node_ids.add(e.source_node_id)
            all_node_ids.add(e.target_node_id)
            if e.source_node_id not in visited:
                new_frontier.add(e.source_node_id)
            if e.target_node_id not in visited:
                new_frontier.add(e.target_node_id)
        visited |= frontier
        frontier = new_frontier - visited

    nodes_res = await db.execute(select(KnowledgeNode).where(KnowledgeNode.id.in_(all_node_ids)))
    nodes = nodes_res.scalars().all()

    edges_res = await db.execute(
        select(KnowledgeEdge).where(
            KnowledgeEdge.source_node_id.in_(all_node_ids) & KnowledgeEdge.target_node_id.in_(all_node_ids)
        )
    )
    edges = edges_res.scalars().all()

    return {
        "nodes": [{"id": n.id, "title": n.title, "content_type": n.content_type} for n in nodes],
        "links": [{"source": e.source_node_id, "target": e.target_node_id, "relationship": e.rel_type, "weight": e.weight} for e in edges],
    }


@router.get("/connections")
async def get_discovered_connections(db: AsyncSession = Depends(get_db)):
    stmt = select(KnowledgeEdge).where(KnowledgeEdge.edge_type == "discovered").order_by(KnowledgeEdge.weight.desc()).limit(50)
    result = await db.execute(stmt)
    edges = result.scalars().all()

    connections = []
    for e in edges:
        src = await db.get(KnowledgeNode, e.source_node_id)
        tgt = await db.get(KnowledgeNode, e.target_node_id)
        if src and tgt:
            connections.append({
                "edge_id": e.id,
                "source": {"id": src.id, "title": src.title},
                "target": {"id": tgt.id, "title": tgt.title},
                "relationship": e.rel_type,
                "strength": e.weight,
                "evidence": e.evidence,
            })
    return connections


@router.post("/edges", response_model=EdgeOut)
async def create_edge(payload: EdgeCreate, db: AsyncSession = Depends(get_db)):
    edge = KnowledgeEdge(
        source_node_id=payload.source_node_id,
        target_node_id=payload.target_node_id,
        rel_type=payload.relationship,
        edge_type="manual",
        evidence=payload.evidence,
    )
    db.add(edge)
    await db.flush()
    await db.refresh(edge)
    return edge


@router.delete("/edges/{edge_id}", status_code=204)
async def delete_edge(edge_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(KnowledgeEdge).where(KnowledgeEdge.id == edge_id))
    edge = result.scalar_one_or_none()
    if not edge:
        raise HTTPException(status_code=404, detail="Edge not found")
    await db.delete(edge)


@router.post("/discover")
async def trigger_discovery(db: AsyncSession = Depends(get_db)):
    """Re-run connection discovery across all existing nodes."""
    from app.services.ingestion.text_processor import TextProcessor
    import re
    from app.services.qa_service import _stem
    from app.models.node import KnowledgeNode

    STOP = {
        "the", "a", "an", "is", "are", "was", "i", "my", "and", "or",
        "to", "for", "of", "in", "on", "at", "it", "its", "this", "that",
        "with", "by", "be", "do", "go", "get", "have", "from", "also",
        "want", "like", "love", "know", "use", "very", "just", "can",
    }

    def keywords(text):
        words = re.findall(r'[a-z]{3,}', text.lower())
        return {_stem(w) for w in words if w not in STOP}

    nodes_res = await db.execute(select(KnowledgeNode))
    nodes = nodes_res.scalars().all()

    new_edges = 0
    for i, node_a in enumerate(nodes):
        for node_b in nodes[i + 1:]:
            kw_a = keywords(node_a.content + " " + node_a.title)
            kw_b = keywords(node_b.content + " " + node_b.title)
            if not kw_a or not kw_b:
                continue
            shared = kw_a & kw_b
            jaccard = len(shared) / len(kw_a | kw_b)
            if jaccard < 0.08:
                continue
            existing = await db.execute(
                select(KnowledgeEdge).where(
                    KnowledgeEdge.source_node_id == node_a.id,
                    KnowledgeEdge.target_node_id == node_b.id,
                    KnowledgeEdge.rel_type == "ENTITY_OVERLAP",
                )
            )
            if existing.scalar_one_or_none():
                continue
            edge = KnowledgeEdge(
                source_node_id=node_a.id,
                target_node_id=node_b.id,
                rel_type="ENTITY_OVERLAP",
                weight=round(jaccard, 3),
                edge_type="discovered",
                evidence=f"Shared keywords: {', '.join(list(shared)[:5])}",
            )
            db.add(edge)
            new_edges += 1

    await db.flush()
    return {"new_edges_created": new_edges}
