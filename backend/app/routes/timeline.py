from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.node import KnowledgeNode
from app.models.tag import NodeTag

router = APIRouter()


@router.get("")
async def get_timeline(
    limit: int = Query(20, le=100),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(KnowledgeNode)
        .options(selectinload(KnowledgeNode.node_tags).selectinload(NodeTag.tag))
        .order_by(KnowledgeNode.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    nodes = result.scalars().all()

    # Group by date
    groups: dict = {}
    for node in nodes:
        date_key = node.created_at.date().isoformat()
        if date_key not in groups:
            groups[date_key] = []
        tags = [{"id": nt.tag.id, "name": nt.tag.name, "color": nt.tag.color} for nt in node.node_tags if nt.tag]
        groups[date_key].append({
            "id": node.id,
            "title": node.title,
            "content_type": node.content_type,
            "excerpt": node.content[:200],
            "word_count": node.word_count,
            "created_at": node.created_at.isoformat(),
            "tags": tags,
        })

    return [{"date": date, "items": items} for date, items in sorted(groups.items(), reverse=True)]
