import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Integer, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _now():
    return datetime.now(timezone.utc)


def _uuid():
    return str(uuid.uuid4())


class KnowledgeNode(Base):
    __tablename__ = "knowledge_nodes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(20), nullable=False, default="note")
    summary: Mapped[str | None] = mapped_column(Text)
    source_url: Mapped[str | None] = mapped_column(Text)
    file_path: Mapped[str | None] = mapped_column(Text)
    word_count: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
    vector_id: Mapped[str | None] = mapped_column(String(36), unique=True)
    extra_metadata: Mapped[dict | None] = mapped_column(JSON, default=dict)

    entities: Mapped[list["Entity"]] = relationship(
        "Entity", back_populates="node", cascade="all, delete-orphan"
    )
    outgoing_edges: Mapped[list["KnowledgeEdge"]] = relationship(
        "KnowledgeEdge",
        foreign_keys="KnowledgeEdge.source_node_id",
        back_populates="source_node",
        cascade="all, delete-orphan",
    )
    incoming_edges: Mapped[list["KnowledgeEdge"]] = relationship(
        "KnowledgeEdge",
        foreign_keys="KnowledgeEdge.target_node_id",
        back_populates="target_node",
        cascade="all, delete-orphan",
    )
    node_tags: Mapped[list["NodeTag"]] = relationship(
        "NodeTag", back_populates="node", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_nodes_content_type", "content_type"),
        Index("idx_nodes_created_at", "created_at"),
    )


class Entity(Base):
    __tablename__ = "entities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    node_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    canonical_name: Mapped[str] = mapped_column(Text, nullable=False)
    start_char: Mapped[int | None] = mapped_column(Integer)
    end_char: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    node: Mapped["KnowledgeNode"] = relationship("KnowledgeNode", back_populates="entities")

    __table_args__ = (
        Index("idx_entities_node_id", "node_id"),
        Index("idx_entities_canonical", "canonical_name"),
    )
