import json
import csv
import os
from datetime import datetime
from typing import List, Dict, Any

class Video:
    def __init__(
        self, video_id: str, desc: str, create_time: int, duration: int,
        digg_count: int, share_count: int, comment_count: int, play_count: int,
        collect_count: int, is_ad: bool
    ) -> None:
        self._video_id = video_id
        self._desc = desc
        self._create_time = datetime.fromtimestamp(create_time).strftime("%Y-%m-%dT%H:%M:%S")
        self._duration = duration
        self._digg_count = digg_count
        self._share_count = share_count
        self._comment_count = comment_count
        self._play_count = play_count
        self._collect_count = collect_count
        self._is_ad = is_ad
    
    @property
    def video_id(self) -> str:
        return self._video_id
    
    @property
    def desc(self) -> str:
        return self._desc
    
    @property
    def create_time(self) -> str:
        return self._create_time
    
    @property
    def duration(self) -> int:
        return self._duration
    
    @property
    def digg_count(self) -> int:
        return self._digg_count
    
    @property
    def share_count(self) -> int:
        return self._share_count
    
    @property
    def comment_count(self) -> int:
        return self._comment_count
    
    @property
    def play_count(self) -> int:
        return self._play_count
    
    @property
    def collect_count(self) -> int:
        return self._collect_count
    
    @property
    def is_ad(self) -> bool:
        return self._is_ad
    
    @property
    def dict(self) -> Dict[str, Any]:
        return {
            "video_id": self.video_id,
            "desc": self.desc,
            "create_time": self.create_time,
            "duration": self.duration,
            "digg_count": self.digg_count,
            "share_count": self.share_count,
            "comment_count": self.comment_count,
            "play_count": self.play_count,
            "collect_count": self.collect_count,
            "is_ad": self.is_ad
        }

    @property
    def json(self) -> str:
        return json.dumps(self.dict, ensure_ascii=False)