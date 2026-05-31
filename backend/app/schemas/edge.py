from typing import Optional
from pydantic import BaseModel, Field


class EdgeCreate(BaseModel):
    source_node_id: str
    target_node_id: str
    relationship: str = "RELATES_TO"
    evidence: Optional[str] = None


class EdgeOut(BaseModel):
    id: str
    source_node_id: str
    target_node_id: str
    relationship: str = Field(alias="rel_type", serialization_alias="relationship")
    weight: float
    edge_type: str
    evidence: Optional[str] = None

    model_config = {"from_attributes": True, "populate_by_name": True}
