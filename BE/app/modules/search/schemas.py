from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SearchQuery(BaseModel):
    keyword: str

class SearchResult(BaseModel):
    keyword: str
    results: List[dict]
    total_count: int
    search_time: float

class SearchHistory(BaseModel):
    keyword: str
    timestamp: datetime
    result_count: int 