from typing import List
from pydantic import BaseModel


class ContentAnalysisCreateSchema(BaseModel):
    source_type: str
    source_id: str
    sentence: str
    aspect_id: int
    sentiment_id: int
    evidence_keywords: List[str]