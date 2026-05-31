from typing import List, Dict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.node import Entity
from app.models.edge import KnowledgeEdge


class GraphBuilder:
    async def link_by_entities(
        self,
        node_id: str,
        entities: List[Dict],
        db: AsyncSession,
    ) -> int:
        if not entities:
            return 0

        canonical_names = [e["canonical_name"] for e in entities]

        # Find other nodes that share entity canonical names
        stmt = (
            select(Entity.node_id)
            .where(
                Entity.canonical_name.in_(canonical_names),
                Entity.node_id != node_id,
            )
            .distinct()
        )
        result = await db.execute(stmt)
        matching_node_ids = result.scalars().all()

        edges_created = 0
        for other_node_id in matching_node_ids:
            # Count shared entities
            shared_stmt = select(Entity).where(
                Entity.canonical_name.in_(canonical_names),
                Entity.node_id == other_node_id,
            )
            shared_res = await db.execute(shared_stmt)
            shared = shared_res.scalars().all()
            if not shared:
                continue

            weight = len(shared) / max(len(canonical_names), 1)

            # Check if edge already exists
            existing = await db.execute(
                select(KnowledgeEdge).where(
                    KnowledgeEdge.source_node_id == node_id,
                    KnowledgeEdge.target_node_id == other_node_id,
                    KnowledgeEdge.rel_type == "MENTIONS_SAME_ENTITY",
                )
            )
            if existing.scalar_one_or_none():
                continue

            edge = KnowledgeEdge(
                source_node_id=node_id,
                target_node_id=other_node_id,
                rel_type="MENTIONS_SAME_ENTITY",
                weight=weight,
                edge_type="auto",
                evidence=f"Shared entities: {', '.join(e['name'] for e in entities[:3])}",
            )
            db.add(edge)
            edges_created += 1

        return edges_created
