from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SentimentOverview(BaseModel):
    total_analyzed: int
    positive_count: int
    negative_count: int
    neutral_count: int
    sentiment_distribution: dict
    time_period: str

class KeywordSentiment(BaseModel):
    keyword: str
    sentiment_score: float
    mention_count: int
    related_keywords: List[str] 