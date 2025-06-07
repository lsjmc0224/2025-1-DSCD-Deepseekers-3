from pydantic import BaseModel
from typing import List, Optional


class VideoSentiment(BaseModel):
    positive: int
    negative: int
    neutral: int


class VideoItem(BaseModel):
    id: str
    title: Optional[str]
    thumbnail_url: Optional[str]
    views: int
    likes: int
    comments: int
    publish_date: str
    is_short: bool
    sentiments: VideoSentiment


class VideoListResponse(BaseModel):
    videos: List[VideoItem]
