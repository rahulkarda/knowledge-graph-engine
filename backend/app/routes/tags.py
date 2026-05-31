from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.tag import Tag, NodeTag
from app.schemas.node import TagOut

router = APIRouter()


class TagCreate(BaseModel):
    name: str
    color: Optional[str] = "#6366f1"


@router.get("", response_model=List[dict])
async def list_tags(db: AsyncSession = Depends(get_db)):
    stmt = select(Tag).order_by(Tag.name)
    result = await db.execute(stmt)
    tags = result.scalars().all()

    tag_list = []
    for tag in tags:
        count_stmt = select(func.count()).select_from(NodeTag).where(NodeTag.tag_id == tag.id)
        count_res = await db.execute(count_stmt)
        count = count_res.scalar_one()
        tag_list.append({"id": tag.id, "name": tag.name, "color": tag.color, "node_count": count})
    return tag_list


@router.post("", response_model=TagOut, status_code=201)
async def create_tag(payload: TagCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Tag).where(Tag.name == payload.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Tag already exists")
    tag = Tag(name=payload.name, color=payload.color or "#6366f1")
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return tag


@router.post("/{tag_id}/nodes/{node_id}", status_code=201)
async def attach_tag(tag_id: str, node_id: str, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(NodeTag).where(NodeTag.tag_id == tag_id, NodeTag.node_id == node_id)
    )
    if existing.scalar_one_or_none():
        return {"message": "Already attached"}
    node_tag = NodeTag(node_id=node_id, tag_id=tag_id)
    db.add(node_tag)
    return {"message": "Tag attached"}


@router.delete("/{tag_id}/nodes/{node_id}", status_code=204)
async def detach_tag(tag_id: str, node_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(NodeTag).where(NodeTag.tag_id == tag_id, NodeTag.node_id == node_id)
    )
    nt = result.scalar_one_or_none()
    if nt:
        await db.delete(nt)
