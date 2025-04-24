from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import Column, String, Float, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class CollectionStatus(Base):
    """
    데이터 수집 작업 상태를 저장하는 모델
    """
    __tablename__ = "collection_status"
    
    id = Column(String, primary_key=True, index=True)
    source = Column(String, nullable=False, index=True)  # youtube, community, instagram 등
    status = Column(String, nullable=False)  # pending, running, completed, failed
    progress = Column(Float, nullable=False, default=0.0)
    message = Column(String)
    params = Column(JSON)  # 수집 파라미터
    result = Column(JSON)  # 수집 결과 요약
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    def __init__(
        self, 
        id: str,
        source: str,
        status: str,
        progress: float = 0.0,
        message: str = "",
        params: Optional[Dict[str, Any]] = None,
        result: Optional[Dict[str, Any]] = None,
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ):
        self.id = id
        self.source = source
        self.status = status
        self.progress = progress
        self.message = message
        self.params = params or {}
        self.result = result
        self.started_at = started_at or datetime.utcnow()
        self.completed_at = completed_at 