"""
YouTube 데이터 모델

이 모듈은 YouTube 동영상, 댓글 및 분석 결과를 저장하기 위한 SQLAlchemy 모델을 정의합니다.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Annotated

from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, 
    Boolean, ForeignKey, JSON, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.base import Base
from app.models.collection_job import CollectionJob  # CollectionJob 모델 임포트


class YouTubeVideo(Base):
    """
    YouTube 동영상 정보 모델
    
    채널 및 동영상 메타데이터를 저장합니다.
    """
    __tablename__ = "youtube_videos"
    __allow_unmapped__ = True
    
    # 기본 식별자는 base에서 상속
    
    # YouTube 동영상 ID (YouTube 플랫폼의 고유 ID)
    youtube_id = Column(String(20), unique=True, nullable=False, index=True)
    
    # 동영상 기본 정보
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=False)
    duration = Column(String(20), nullable=True)  # ISO 8601 형식 (PT1H2M3S)
    
    # 채널 정보
    channel_id = Column(String(50), nullable=False, index=True)
    channel_title = Column(String(255), nullable=False)
    
    # 통계 정보
    view_count = Column(Integer, nullable=False, default=0)
    like_count = Column(Integer, nullable=False, default=0)
    comment_count = Column(Integer, nullable=False, default=0)
    
    # 추가 메타데이터
    thumbnail_url = Column(String(255), nullable=True)
    tags = Column(JSON, nullable=True)
    category_id = Column(String(10), nullable=True)
    
    # 수집 및 상태 정보
    last_fetched_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # 관계
    comments: Mapped[List["YouTubeComment"]] = relationship("YouTubeComment", back_populates="video", cascade="all, delete-orphan")
    sentiment_analysis: Mapped[Optional["YouTubeSentimentAnalysis"]] = relationship("YouTubeSentimentAnalysis", back_populates="video", uselist=False, cascade="all, delete-orphan")
    
    # 인덱스 및 제약조건
    __table_args__ = (
        Index("ix_youtube_videos_channel_published", "channel_id", "published_at"),
    )
    
    def __repr__(self) -> str:
        return f"<YouTubeVideo(id='{self.id}', youtube_id='{self.youtube_id}', title='{self.title}')>"


class YouTubeComment(Base):
    """
    YouTube 댓글 정보 모델
    
    동영상 댓글 및 관련 메타데이터를 저장합니다.
    """
    __tablename__ = "youtube_comments"
    __allow_unmapped__ = True
    
    # 기본 식별자는 base에서 상속
    
    # 외래 키
    video_id = Column(String(36), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # YouTube 댓글 ID (YouTube 플랫폼의 고유 ID)
    comment_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # 댓글 내용
    text = Column(Text, nullable=False)
    
    # 작성자 정보
    author_name = Column(String(100), nullable=False)
    author_channel_id = Column(String(50), nullable=True)
    author_profile_url = Column(String(255), nullable=True)
    
    # 통계 및 메타데이터
    like_count = Column(Integer, nullable=False, default=0)
    published_at = Column(DateTime, nullable=False)
    is_reply = Column(Boolean, nullable=False, default=False)
    parent_id = Column(String(50), nullable=True)  # 답글인 경우 부모 댓글 ID
    
    # 감성 분석 결과
    sentiment_score = Column(Float, nullable=True)
    sentiment_label = Column(String(20), nullable=True)
    
    # 관계
    video: Mapped["YouTubeVideo"] = relationship("YouTubeVideo", back_populates="comments")
    
    # 인덱스 및 제약조건
    __table_args__ = (
        Index("ix_youtube_comments_sentiment", "sentiment_label", "sentiment_score"),
    )
    
    def __repr__(self) -> str:
        return f"<YouTubeComment(id='{self.id}', author='{self.author_name}', sentiment='{self.sentiment_label}')>"


class YouTubeSentimentAnalysis(Base):
    """
    YouTube 동영상 감성 분석 결과 모델
    
    동영상 전체에 대한 감성 분석 요약 정보를 저장합니다.
    """
    __tablename__ = "youtube_sentiment_analysis"
    __allow_unmapped__ = True
    
    # 기본 식별자는 base에서 상속
    
    # 외래 키
    video_id = Column(String(36), ForeignKey("youtube_videos.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    # 감성 분석 요약
    positive_count = Column(Integer, nullable=False, default=0)
    negative_count = Column(Integer, nullable=False, default=0)
    neutral_count = Column(Integer, nullable=False, default=0)
    
    # 백분율 통계
    positive_percentage = Column(Float, nullable=False, default=0.0)
    negative_percentage = Column(Float, nullable=False, default=0.0)
    neutral_percentage = Column(Float, nullable=False, default=0.0)
    
    # 평균 감성 점수
    average_sentiment_score = Column(Float, nullable=False, default=0.0)
    
    # 핵심 키워드 (JSON 형식으로 저장)
    positive_keywords = Column(JSON, nullable=True)
    negative_keywords = Column(JSON, nullable=True)
    
    # 분석 메타데이터
    analyzed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    analysis_version = Column(String(20), nullable=True)  # 분석에 사용된 모델 버전
    
    # 관계
    video: Mapped["YouTubeVideo"] = relationship("YouTubeVideo", back_populates="sentiment_analysis")
    
    def __repr__(self) -> str:
        return f"<YouTubeSentimentAnalysis(video_id='{self.video_id}', average_score='{self.average_sentiment_score}')>" 