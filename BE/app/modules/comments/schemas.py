from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class CommentAnalysis(BaseModel):
    sentiment_score: float
    aspect: str


class Comment(BaseModel):
    id: str
    text: str
    date: datetime
    sentiment: str
    source: str
    likes: Optional[int]
    attributes: List[str]
    analysis: CommentAnalysis
