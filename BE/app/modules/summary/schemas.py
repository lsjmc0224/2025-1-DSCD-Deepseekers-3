from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class WeeklyChange(BaseModel):
    week_start: datetime
    week_end: datetime
    change_percentage: float
    platform: str

class DailyStats(BaseModel):
    date: datetime
    total_comments: int
    positive_comments: int
    negative_comments: int
    neutral_comments: int

class PlatformSentiment(BaseModel):
    platform: str
    positive_percentage: float
    negative_percentage: float
    neutral_percentage: float 