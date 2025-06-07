from pydantic import BaseModel
from typing import List, Dict


class SummaryChange(BaseModel):
    positive_change: str  # e.g., "+1.23%"
    positive_delta: str   # e.g., "0.42%"
    negative_change: str  # e.g., "-0.18%"
    negative_delta: str   # e.g., "0.06%"
    total_change: str     # e.g., "+38"
    total_delta: str      # e.g., "1.58%"


class SentimentDistributionItem(BaseModel):
    positive: int
    neutral: int
    negative: int


class SentimentTrendItem(BaseModel):
    date: str  # e.g., "2024-10-01"
    positive: int
    neutral: int
    negative: int


class SummaryOverviewResponse(BaseModel):
    summary_change: SummaryChange
    sentiment_distribution: Dict[str, SentimentDistributionItem]
    sentiment_trend: List[SentimentTrendItem]
