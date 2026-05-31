from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.node import KnowledgeNode
from app.models.tag import NodeTag, Tag
from app.schemas.node import NodeDetail, NodeSummary, NodeUpdate

router = APIRouter()


def _build_node_summary(node: KnowledgeNode) -> NodeSummary:
    tags = [nt.tag for nt in (node.node_tags or []) if nt.tag]
    return NodeSummary(
        id=node.id,
        title=node.title,
        content_type=node.content_type,
        word_count=node.word_count,
        created_at=node.created_at,
        tags=[{"id": t.id, "name": t.name, "color": t.color} for t in tags],
    )


@router.get("", response_model=List[NodeSummary])
async def list_nodes(
    content_type: Optional[str] = Query(None),
    tag_id: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(KnowledgeNode)
        .options(
            selectinload(KnowledgeNode.node_tags).selectinload(NodeTag.tag)
        )
        .order_by(KnowledgeNode.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    if content_type:
        stmt = stmt.where(KnowledgeNode.content_type == content_type)
    if tag_id:
        stmt = stmt.join(KnowledgeNode.node_tags).where(NodeTag.tag_id == tag_id)

    result = await db.execute(stmt)
    nodes = result.scalars().all()
    return [_build_node_summary(n) for n in nodes]


@router.get("/{node_id}", response_model=NodeDetail)
async def get_node(node_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(KnowledgeNode)
        .where(KnowledgeNode.id == node_id)
        .options(
            selectinload(KnowledgeNode.entities),
            selectinload(KnowledgeNode.node_tags).selectinload(NodeTag.tag),
            selectinload(KnowledgeNode.outgoing_edges),
            selectinload(KnowledgeNode.incoming_edges),
        )
    )
    result = await db.execute(stmt)
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    tags = [{"id": nt.tag.id, "name": nt.tag.name, "color": nt.tag.color} for nt in node.node_tags if nt.tag]
    return NodeDetail(
        id=node.id,
        title=node.title,
        content=node.content,
        content_type=node.content_type,
        summary=node.summary,
        source_url=node.source_url,
        file_path=node.file_path,
        word_count=node.word_count,
        created_at=node.created_at,
        updated_at=node.updated_at,
        entities=node.entities,
        tags=tags,
        outgoing_edges=node.outgoing_edges,
        incoming_edges=node.incoming_edges,
    )


@router.put("/{node_id}", response_model=NodeDetail)
async def update_node(node_id: str, payload: NodeUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(KnowledgeNode).where(KnowledgeNode.id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    if payload.title is not None:
        node.title = payload.title
    if payload.content is not None:
        node.content = payload.content
        node.word_count = len(payload.content.split())
    node.updated_at = datetime.utcnow()
    return await get_node(node_id, db)


@router.delete("/{node_id}", status_code=204)
async def delete_node(node_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(KnowledgeNode).where(KnowledgeNode.id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    await db.delete(node)


@router.get("/{node_id}/neighbors", response_model=List[NodeSummary])
async def get_neighbors(node_id: str, db: AsyncSession = Depends(get_db)):
    from app.models.edge import KnowledgeEdge

    stmt_out = select(KnowledgeEdge.target_node_id).where(KnowledgeEdge.source_node_id == node_id)
    stmt_in = select(KnowledgeEdge.source_node_id).where(KnowledgeEdge.target_node_id == node_id)

    out_ids = (await db.execute(stmt_out)).scalars().all()
    in_ids = (await db.execute(stmt_in)).scalars().all()
    neighbor_ids = list(set(out_ids) | set(in_ids))

    if not neighbor_ids:
        return []

    stmt = (
        select(KnowledgeNode)
        .where(KnowledgeNode.id.in_(neighbor_ids))
        .options(selectinload(KnowledgeNode.node_tags).selectinload(NodeTag.tag))
    )
    result = await db.execute(stmt)
    return [_build_node_summary(n) for n in result.scalars().all()]
