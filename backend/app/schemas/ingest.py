from typing import Optional
from pydantic import BaseModel, HttpUrl


class NoteIngest(BaseModel):
    title: str
    content: str


class UrlIngest(BaseModel):
    url: str
    title: Optional[str] = None


class IngestResponse(BaseModel):
    node_id: str
    title: str
    content_type: str
    word_count: int
    entities_found: int
    edges_created: int
    tags_applied: int
    message: str = "Ingested successfully"
