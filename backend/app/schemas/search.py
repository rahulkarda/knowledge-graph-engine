from typing import Optional, List
from pydantic import BaseModel


class SemanticSearchRequest(BaseModel):
    query: str
    top_k: int = 10
    content_type: Optional[str] = None


class SearchResult(BaseModel):
    node_id: str
    title: str
    content_type: str
    excerpt: str
    score: float
    created_at: str


class SemanticSearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int
