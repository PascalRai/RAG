from uuid import UUID
from typing import Any, Dict, List
from pydantic import BaseModel

class RetreivalRequest(BaseModel):
    index_name: str = "test_01"
    query: str = "How has Apple's total net sales changed over time?"
    top_k: int = 10


class RetrievedPoint(BaseModel):
    id: UUID
    score: float
    metadata: Dict[str, Any]
    text: str


class RetrievalResponse(BaseModel):
    results: List[RetrievedPoint]