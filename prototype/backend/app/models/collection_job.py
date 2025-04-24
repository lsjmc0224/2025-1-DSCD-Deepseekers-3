"""
데이터 수집 작업 모델

데이터 수집 작업 상태를 추적하기 위한 모델입니다.
"""

from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import Column, String, Float, JSON, DateTime, Text
from sqlalchemy.sql import func

from app.db.base import Base


class CollectionJob(Base):
    """데이터 수집 작업 모델"""
    
    __tablename__ = "collection_jobs"
    
    id = Column(String(50), primary_key=True, index=True)
    type = Column(String(50), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True, 
                   default="initialized")  # initialized, running, completed, failed
    parameters = Column(JSON, nullable=True)
    progress = Column(Float, nullable=False, default=0.0)
    message = Column(Text, nullable=True)
    result = Column(JSON, nullable=True)
    started_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self) -> str:
        return f"<CollectionJob(id={self.id}, type={self.type}, status={self.status})>" 