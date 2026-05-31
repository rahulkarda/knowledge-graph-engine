import re
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.node import KnowledgeNode, Entity
from app.models.edge import KnowledgeEdge
from app.schemas.ingest import IngestResponse


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


class TextProcessor:
    async def process(
        self,
        title: str,
        content: str,
        content_type: str,
        db: AsyncSession,
        source_url: Optional[str] = None,
        file_path: Optional[str] = None,
    ) -> IngestResponse:
        content = clean_text(content)
        word_count = len(content.split())

        node = KnowledgeNode(
            title=title,
            content=content,
            content_type=content_type,
            word_count=word_count,
            source_url=source_url,
            file_path=file_path,
        )
        db.add(node)
        await db.flush()

        entities_found = 0
        edges_created = 0
        tags_applied = 0

        # NLP pipeline — regex extractor always runs; spaCy used if installed
        try:
            from app.services.nlp.entity_extractor import EntityExtractor
            from app.services.nlp.auto_tagger import AutoTagger
            from app.services.graph.graph_builder import GraphBuilder
            from app.models.tag import Tag, NodeTag
            from sqlalchemy import select

            extractor = EntityExtractor()
            tagger = AutoTagger()
            builder = GraphBuilder()

            extracted = extractor.extract(content + " " + title)
            for e in extracted:
                entity = Entity(
                    node_id=node.id,
                    name=e["name"],
                    entity_type=e["entity_type"],
                    canonical_name=e["canonical_name"],
                    start_char=e.get("start_char"),
                    end_char=e.get("end_char"),
                )
                db.add(entity)
            entities_found = len(extracted)

            auto_tags = tagger.suggest(content, extracted)
            for tag_name in auto_tags[:5]:
                res = await db.execute(select(Tag).where(Tag.name == tag_name))
                tag = res.scalar_one_or_none()
                if not tag:
                    tag = Tag(name=tag_name, is_auto=True)
                    db.add(tag)
                    await db.flush()
                # Avoid duplicate node_tags
                existing_nt = await db.execute(
                    select(NodeTag).where(NodeTag.node_id == node.id, NodeTag.tag_id == tag.id)
                )
                if not existing_nt.scalar_one_or_none():
                    nt = NodeTag(node_id=node.id, tag_id=tag.id)
                    db.add(nt)
                    tags_applied += 1

            await db.flush()
            edges_created = await builder.link_by_entities(node.id, extracted, db)

        except Exception:
            pass

        # Vector embedding — only if sentence-transformers + Qdrant available
        try:
            from app.services.embedding_service import EmbeddingService
            from app.services.vector_store import VectorStore
            from app.utils.text_utils import chunk_text

            embedding_service = EmbeddingService()
            vector_store = VectorStore()

            chunks = chunk_text(content)
            embeddings = [embedding_service.embed_text(c) for c in chunks]
            vector_store.upsert(
                node_id=node.id,
                chunks=chunks,
                embeddings=embeddings,
                metadata={
                    "node_id": node.id,
                    "title": title,
                    "content_type": content_type,
                },
            )
            node.vector_id = node.id

            try:
                from app.services.graph.connection_discovery import ConnectionDiscovery
                query_emb = embedding_service.embed_text(content[:1000])
                hits = vector_store.search(query_emb, top_k=10)
                discovery = ConnectionDiscovery()
                sem_edges = await discovery.create_semantic_edges(node.id, hits, db)
                edges_created += sem_edges
            except Exception:
                pass

        except Exception:
            pass

        # Score-based connection discovery (no ML needed) — runs always
        try:
            await self._discover_text_connections(node.id, content, title, db)
        except Exception:
            pass

        await db.flush()

        return IngestResponse(
            node_id=node.id,
            title=title,
            content_type=content_type,
            word_count=word_count,
            entities_found=entities_found,
            edges_created=edges_created,
            tags_applied=tags_applied,
        )

    async def _discover_text_connections(self, node_id: str, content: str, title: str, db: AsyncSession):
        """
        Lightweight connection discovery that runs without any ML libraries.
        Links notes that share significant keyword overlap.
        """
        from sqlalchemy import select
        from app.models.node import KnowledgeNode
        from app.models.edge import KnowledgeEdge
        from app.services.qa_service import _stem

        STOP = {
            "the", "a", "an", "is", "are", "was", "i", "my", "and", "or",
            "to", "for", "of", "in", "on", "at", "it", "its", "this", "that",
            "with", "by", "be", "do", "go", "get", "have", "from", "also",
            "want", "like", "love", "know", "use", "very", "just", "can",
        }

        def keywords(text):
            words = re.findall(r'[a-z]{3,}', text.lower())
            return {_stem(w) for w in words if w not in STOP}

        new_kw = keywords(content + " " + title)
        if not new_kw:
            return

        stmt = select(KnowledgeNode).where(KnowledgeNode.id != node_id)
        res = await db.execute(stmt)
        other_nodes = res.scalars().all()

        for other in other_nodes:
            other_kw = keywords(other.content + " " + other.title)
            if not other_kw:
                continue

            shared = new_kw & other_kw
            jaccard = len(shared) / len(new_kw | other_kw)

            if jaccard < 0.08:
                continue

            # Check edge doesn't already exist
            existing = await db.execute(
                select(KnowledgeEdge).where(
                    KnowledgeEdge.source_node_id == node_id,
                    KnowledgeEdge.target_node_id == other.id,
                    KnowledgeEdge.rel_type == "ENTITY_OVERLAP",
                )
            )
            if existing.scalar_one_or_none():
                continue

            evidence = f"Shared keywords: {', '.join(list(shared)[:5])}"
            edge = KnowledgeEdge(
                source_node_id=node_id,
                target_node_id=other.id,
                rel_type="ENTITY_OVERLAP",
                weight=round(jaccard, 3),
                edge_type="discovered",
                evidence=evidence,
            )
            db.add(edge)
