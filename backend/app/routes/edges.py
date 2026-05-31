from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.edge import KnowledgeEdge
from app.schemas.edge import EdgeCreate, EdgeOut

router = APIRouter()


@router.post("", response_model=EdgeOut, status_code=201)
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


@router.delete("/{edge_id}", status_code=204)
async def delete_edge(edge_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(KnowledgeEdge).where(KnowledgeEdge.id == edge_id))
    edge = result.scalar_one_or_none()
    if not edge:
        raise HTTPException(status_code=404, detail="Edge not found")
    await db.delete(edge)
