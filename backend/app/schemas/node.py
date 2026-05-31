from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class EntityOut(BaseModel):
    id: str
    name: str
    entity_type: str
    canonical_name: str
    start_char: Optional[int] = None
    end_char: Optional[int] = None

    model_config = {"from_attributes": True}


class TagOut(BaseModel):
    id: str
    name: str
    color: str

    model_config = {"from_attributes": True}


class EdgeOut(BaseModel):
    id: str
    source_node_id: str
    target_node_id: str
    relationship: str = Field(alias="rel_type", serialization_alias="relationship")
    weight: float
    edge_type: str
    evidence: Optional[str] = None

    model_config = {"from_attributes": True, "populate_by_name": True}


class NodeSummary(BaseModel):
    id: str
    title: str
    content_type: str
    word_count: Optional[int] = None
    created_at: datetime
    tags: List[TagOut] = []

    model_config = {"from_attributes": True}


class NodeDetail(BaseModel):
    id: str
    title: str
    content: str
    content_type: str
    summary: Optional[str] = None
    source_url: Optional[str] = None
    file_path: Optional[str] = None
    word_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    entities: List[EntityOut] = []
    tags: List[TagOut] = []
    outgoing_edges: List[EdgeOut] = []
    incoming_edges: List[EdgeOut] = []

    model_config = {"from_attributes": True}


class NodeUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
