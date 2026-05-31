import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _now():
    return datetime.now(timezone.utc)


def _uuid():
    return str(uuid.uuid4())


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    color: Mapped[str] = mapped_column(String(7), default="#6366f1")
    is_auto: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    node_tags: Mapped[list["NodeTag"]] = relationship(
        "NodeTag", back_populates="tag", cascade="all, delete-orphan"
    )


class NodeTag(Base):
    __tablename__ = "node_tags"

    node_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("knowledge_nodes.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )

    node: Mapped["KnowledgeNode"] = relationship("KnowledgeNode", back_populates="node_tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="node_tags")

    __table_args__ = (Index("idx_node_tags_tag", "tag_id"),)
