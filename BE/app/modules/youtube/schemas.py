from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VideoBase(BaseModel):
    video_id: str
    title: str
    channel_id: str
    channel_title: str
    view_count: int
    like_count: int
    comment_count: int
    published_at: datetime
    sentiment_score: float

class Video(VideoBase):
    duration: str
    description: Optional[str]
    tags: Optional[list[str]]

class ShortVideo(VideoBase):
    pass 