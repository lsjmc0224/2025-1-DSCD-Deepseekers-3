from pydantic import BaseModel
from typing import List
from datetime import datetime



class AttributeSentimentItem(BaseModel):
    name: str
    긍정: int
    부정: int


class SentimentOverviewResponse(BaseModel):
    summary: str
    positive_keywords: List[str]
    negative_keywords: List[str]
    attribute_sentiment: List[AttributeSentimentItem]

class CommentItem(BaseModel):
    id: str
    text: str
    date: datetime
    sentiment: str  # "positive" or "negative"
    source: str     # 예: "유튜브", "커뮤니티", "틱톡"
    likes: int


class SentimentDetailsSection(BaseModel):
    summary: str
    comments: List[CommentItem]


class SentimentDetailsResponse(BaseModel):
    positive: SentimentDetailsSection
    negative: SentimentDetailsSection