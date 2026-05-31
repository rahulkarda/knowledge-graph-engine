from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.node import KnowledgeNode
from app.schemas.qa import QAResponse, SourceNode


def _stem(w: str) -> str:
    """Minimal suffix-stripping stem so 'hobbies'→'hobbi', 'morning'→'morni'."""
    for suffix in ("ies", "ing", "tion", "ed", "ly", "es", "s"):
        if w.endswith(suffix) and len(w) - len(suffix) >= 3:
            return w[: len(w) - len(suffix)]
    return w


_QUERY_STOP = {
    "what", "are", "my", "is", "the", "a", "an", "do", "i", "how", "tell",
    "me", "about", "some", "any", "have", "know", "does", "did", "can",
    "which", "who", "when", "where", "why", "would", "could", "should",
    "please", "list", "show", "give", "find",
}


def _score(query: str, title: str, content: str) -> float:
    """
    TF-style relevance score: how well does this node answer the query?
    Weights: title match > stem match > substring match.
    Query stopwords (what/are/my/is/…) are excluded so they don't skew results.
    Returns 0.0–1.0.
    """
    raw = [w.lower().strip("?!.,;:'\"") for w in query.split()]
    q_words = [w for w in raw if len(w) >= 2 and w not in _QUERY_STOP]
    if not q_words:
        # All words were stopwords — fall back to full word list
        q_words = [w for w in raw if len(w) >= 2]
    if not q_words:
        return 0.0

    text = (title + " " + content).lower()
    title_lower = title.lower()
    title_stems = {_stem(t) for t in title_lower.split()}
    text_stems = {_stem(t) for t in text.split()}
    q_stems = [_stem(w) for w in q_words]

    score = 0.0
    for word, stem in zip(q_words, q_stems):
        if word in title_lower:
            score += 4.0
        elif stem in title_stems:
            score += 2.5
        if word in text:
            score += 1.0
        elif stem in text_stems:
            score += 0.5

    return round(score / (len(q_words) * 5), 4)  # normalise to 0-1


class QAService:
    def __init__(self):
        self._pipeline = None

    @property
    def pipeline(self):
        if self._pipeline is None:
            from transformers import pipeline as hf_pipeline
            from app.config import settings
            self._pipeline = hf_pipeline(
                "text2text-generation",
                model=settings.qa_model,
                max_new_tokens=200,
            )
        return self._pipeline

    async def answer(self, question: str, top_k: int, db: AsyncSession) -> QAResponse:
        hits = await self._retrieve(question, top_k, db)

        if not hits:
            return QAResponse(
                question=question,
                answer="I don't have enough information in your knowledge base to answer that yet. Try adding more notes first.",
                sources=[],
            )

        context_parts = []
        sources = []
        for hit in hits:
            node_id = hit["node_id"]
            excerpt = hit["text"][:500]
            score = hit.get("score", 1.0)

            stmt = select(KnowledgeNode).where(KnowledgeNode.id == node_id)
            res = await db.execute(stmt)
            node = res.scalar_one_or_none()
            if node:
                context_parts.append(f"[{node.title}]: {node.content}")
                sources.append(SourceNode(node_id=node_id, title=node.title, excerpt=excerpt, score=score))

        context = "\n\n".join(context_parts)
        answer_text = self._generate(context, question, sources)

        return QAResponse(question=question, answer=answer_text, sources=sources)

    async def _retrieve(self, question: str, top_k: int, db: AsyncSession) -> list:
        # Try semantic vector search first
        try:
            from app.services.embedding_service import EmbeddingService
            from app.services.vector_store import VectorStore

            embedding_service = EmbeddingService()
            vector_store = VectorStore()
            query_embedding = embedding_service.embed_text(question)
            hits = vector_store.search(query_embedding, top_k=top_k)
            if hits:
                return hits
        except Exception:
            pass

        # Fallback: TF-style scored search across all nodes
        stmt = select(KnowledgeNode).order_by(KnowledgeNode.created_at.desc()).limit(500)
        res = await db.execute(stmt)
        nodes = res.scalars().all()

        scored = []
        for node in nodes:
            s = _score(question, node.title, node.content)
            scored.append((s, node))

        scored.sort(key=lambda x: x[0], reverse=True)

        # Always return at least top_k results even if scores are 0
        # (small KB — better to answer from context than refuse)
        pool = scored[:top_k] if any(s > 0 for s, _ in scored) else scored[:top_k]

        return [
            {"node_id": n.id, "text": n.content[:500], "score": s}
            for s, n in pool
        ]

    def _generate(self, context: str, question: str, sources: list) -> str:
        # Try flan-t5 if available
        try:
            prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
            output = self.pipeline(prompt, max_new_tokens=200)
            return output[0]["generated_text"].strip()
        except Exception:
            pass

        # Extractive fallback using the already-ranked sources list
        # sources are already sorted by relevance score
        if sources:
            best = sources[0]
            # Find the most relevant sentence inside the best source
            sentences = [s.strip() for s in best.excerpt.replace("\n", ". ").split(".") if len(s.strip()) > 10]
            if sentences:
                q_words = set(question.lower().strip("?!.,").split())
                best_sent = max(sentences, key=lambda s: sum(1 for w in q_words if _stem(w) in _stem(s.lower())))
                return f'Based on your note "{best.title}": {best_sent}.'
            return f'Based on your note "{best.title}": {best.excerpt.strip()}.'

        return "I couldn't find a relevant answer in your knowledge base."
