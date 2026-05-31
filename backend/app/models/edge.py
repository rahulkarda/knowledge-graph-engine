import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Float, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship as sa_relationship

from app.database import Base


def _now():
    return datetime.now(timezone.utc)


def _uuid():
    return str(uuid.uuid4())


class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    source_node_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), nullable=False
    )
    target_node_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), nullable=False
    )
    rel_type: Mapped[str] = mapped_column(String(100), nullable=False, default="RELATES_TO")
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    edge_type: Mapped[str] = mapped_column(String(20), default="auto")
    evidence: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    source_node: Mapped["KnowledgeNode"] = sa_relationship(
        "KnowledgeNode",
        foreign_keys=[source_node_id],
        back_populates="outgoing_edges",
    )
    target_node: Mapped["KnowledgeNode"] = sa_relationship(
        "KnowledgeNode",
        foreign_keys=[target_node_id],
        back_populates="incoming_edges",
    )

    __table_args__ = (
        UniqueConstraint("source_node_id", "target_node_id", "rel_type", name="uq_edge"),
        Index("idx_edges_source", "source_node_id"),
        Index("idx_edges_target", "target_node_id"),
    )
