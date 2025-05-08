from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Comment(BaseModel):
    id: str
    content: str
    platform: str
    sentiment: str
    created_at: datetime
    author: Optional[str]
    likes: Optional[int]
    replies: Optional[int] 