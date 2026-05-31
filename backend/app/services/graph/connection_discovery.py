from typing import List, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.edge import KnowledgeEdge
from app.config import settings


class ConnectionDiscovery:
    async def create_semantic_edges(
        self,
        node_id: str,
        hits: List[Dict],
        db: AsyncSession,
    ) -> int:
        edges_created = 0
        for hit in hits:
            other_id = hit.get("node_id")
            score = hit.get("score", 0.0)

            if not other_id or other_id == node_id:
                continue
            if score < settings.semantic_similarity_threshold:
                continue

            # Avoid duplicate edges
            existing = await db.execute(
                select(KnowledgeEdge).where(
                    KnowledgeEdge.source_node_id == node_id,
                    KnowledgeEdge.target_node_id == other_id,
                    KnowledgeEdge.rel_type == "SIMILAR_TO",
                )
            )
            if existing.scalar_one_or_none():
                continue

            edge = KnowledgeEdge(
                source_node_id=node_id,
                target_node_id=other_id,
                rel_type="SIMILAR_TO",
                weight=score,
                edge_type="semantic",
                evidence=f"Semantic similarity: {score:.3f}",
            )
            db.add(edge)
            edges_created += 1

        return edges_created

    async def run_discovery(self, db: AsyncSession) -> int:
        """Full discovery pass — Jaccard + semantic + path analysis."""
        from app.models.node import KnowledgeNode, Entity
        from sqlalchemy import select, func

        # Load all nodes
        nodes_res = await db.execute(select(KnowledgeNode.id))
        node_ids = nodes_res.scalars().all()

        if len(node_ids) < 2:
            return 0

        total_new_edges = 0

        # Jaccard entity overlap for every pair
        for i, id_a in enumerate(node_ids):
            for id_b in node_ids[i + 1:]:
                ents_a = set(
                    r[0] for r in (await db.execute(
                        select(Entity.canonical_name).where(Entity.node_id == id_a)
                    )).all()
                )
                ents_b = set(
                    r[0] for r in (await db.execute(
                        select(Entity.canonical_name).where(Entity.node_id == id_b)
                    )).all()
                )
                if not ents_a or not ents_b:
                    continue

                intersection = ents_a & ents_b
                union = ents_a | ents_b
                jaccard = len(intersection) / len(union)

                if jaccard < settings.jaccard_threshold:
                    continue

                # Check existing edge
                existing = await db.execute(
                    select(KnowledgeEdge).where(
                        KnowledgeEdge.source_node_id == id_a,
                        KnowledgeEdge.target_node_id == id_b,
                        KnowledgeEdge.rel_type == "ENTITY_OVERLAP",
                    )
                )
                if existing.scalar_one_or_none():
                    continue

                evidence = f"Shared concepts: {', '.join(list(intersection)[:3])}"
                edge = KnowledgeEdge(
                    source_node_id=id_a,
                    target_node_id=id_b,
                    rel_type="ENTITY_OVERLAP",
                    weight=jaccard,
                    edge_type="discovered",
                    evidence=evidence,
                )
                db.add(edge)
                total_new_edges += 1

        await db.flush()
        return total_new_edges
