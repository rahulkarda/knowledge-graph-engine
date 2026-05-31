from typing import List, Optional
from pydantic import BaseModel


class QARequest(BaseModel):
    question: str
    top_k: int = 5


class SourceNode(BaseModel):
    node_id: str
    title: str
    excerpt: str
    score: float


class QAResponse(BaseModel):
    question: str
    answer: str
    sources: List[SourceNode]
