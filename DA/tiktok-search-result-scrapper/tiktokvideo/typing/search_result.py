import json
from typing import List, Any, Dict
from .video import Video

class SearchResult:
    def __init__(
        self, videos: List['Video'], has_more: bool, cursor: int, keyword: str
    ) -> None:
        self._videos: List['Video'] = videos if videos else []  # ✅ None 체크 추가
        self._has_more: bool = has_more
        self._cursor: int = cursor
        self._keyword: str = keyword
    
    @property
    def videos(self) -> List['Video']:
        return self._videos
    
    @property
    def has_more(self) -> bool:
        return self._has_more
    
    @property
    def cursor(self) -> int:
        return self._cursor
    
    @property
    def keyword(self) -> str:
        return self._keyword
    
    @property
    def dict(self) -> Dict[str, Any]:
        return {
            "videos": [video.dict if isinstance(video, Video) else video for video in self._videos],
            "has_more": self._has_more,
            "cursor": self._cursor,
            "keyword": self._keyword
        }
    
    @property
    def json(self) -> str:
        return json.dumps(self.dict, ensure_ascii=False, default=str)  # ✅ JSON 변환 안전성 추가
    
    def __str__(self) -> str:
        return self.json
