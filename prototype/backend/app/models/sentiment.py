"""
감성 분석 결과를 저장하는 데이터베이스 모델

KR-BERT 감성 분석 결과 및 메타데이터를 PostgreSQL에 효율적으로 저장하기 위한 모델입니다.
시계열 데이터 저장과 효율적인 쿼리를 위한 인덱스가 포함되어 있습니다.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, Text, JSON, Index, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, validates, DeclarativeBase, mapped_column, Mapped

# SQLAlchemy 2.0 스타일의 기본 클래스 정의
class Base(DeclarativeBase):
    pass


class SentimentBatch(Base):
    """
    감성 분석 배치 작업 정보를 저장하는 모델
    
    여러 텍스트에 대한 감성 분석을 일괄 처리할 때 사용되는 배치 정보를 기록합니다.
    각 배치는 여러 개의 SentimentAnalysis 인스턴스와 연결됩니다.
    """
    __tablename__ = "sentiment_batches"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String(36), unique=True, index=True, nullable=False, comment="배치 작업 고유 ID (UUID)")
    source = Column(String(50), index=True, nullable=False, comment="데이터 소스 (예: youtube, instagram, survey)")
    description = Column(String(255), nullable=True, comment="배치 작업 설명")
    total_items = Column(Integer, default=0, comment="처리된 총 항목 수")
    processed_items = Column(Integer, default=0, comment="성공적으로 처리된 항목 수")
    failed_items = Column(Integer, default=0, comment="처리 실패한 항목 수")
    status = Column(String(20), index=True, default="pending", comment="배치 상태 (pending, processing, completed, failed)")
    created_at = Column(DateTime, default=func.now(), index=True, comment="배치 생성 시간")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="배치 최종 업데이트 시간")
    completed_at = Column(DateTime, nullable=True, comment="배치 완료 시간")
    duration_seconds = Column(Float, nullable=True, comment="처리 소요 시간 (초)")
    additional_info = Column(JSONB, nullable=True, comment="추가 메타데이터")
    
    # 관계 설정: 한 배치에 여러 분석 결과가 연결됨
    analyses = relationship("SentimentAnalysis", back_populates="batch", cascade="all, delete-orphan")
    
    # 복합 인덱스 추가 - 날짜 기반 쿼리 최적화
    __table_args__ = (
        Index('ix_sentiment_batches_source_created', source, created_at.desc()),
        Index('ix_sentiment_batches_status_created', status, created_at.desc()),
    )
    
    @validates('status')
    def validate_status(self, key, status):
        """상태 값 검증"""
        allowed_statuses = ['pending', 'processing', 'completed', 'failed']
        if status not in allowed_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {allowed_statuses}")
        return status


class SentimentAnalysis(Base):
    """
    개별 텍스트에 대한 감성 분석 결과를 저장하는 모델
    
    각 텍스트 항목의 감성 분석 결과 및 관련 메타데이터를 저장합니다.
    시간별 추세 분석을 위한 시계열 데이터 구조가 포함됩니다.
    """
    __tablename__ = "sentiment_analyses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String(36), ForeignKey("sentiment_batches.batch_id"), index=True, nullable=False, comment="연결된 배치 ID")
    text_id = Column(String(100), index=True, nullable=False, comment="분석된 텍스트의 고유 ID (예: 댓글 ID)")
    text_type = Column(String(50), index=True, nullable=False, comment="텍스트 유형 (예: comment, review, post)")
    original_text = Column(Text, nullable=True, comment="원본 텍스트")
    processed_text = Column(Text, nullable=True, comment="전처리된 텍스트")
    
    # 감성 분석 결과
    sentiment = Column(String(20), index=True, nullable=False, comment="감성 판정 (positive, neutral, negative)")
    positive_score = Column(Float, nullable=False, default=0.0, comment="긍정 점수 (0-1)")
    neutral_score = Column(Float, nullable=False, default=0.0, comment="중립 점수 (0-1)")
    negative_score = Column(Float, nullable=False, default=0.0, comment="부정 점수 (0-1)")
    confidence = Column(Float, nullable=False, default=0.0, comment="신뢰도 점수 (0-1)")
    
    # 시간 관련 필드
    analyzed_at = Column(DateTime, default=func.now(), index=True, comment="분석 시간")
    source_created_at = Column(DateTime, nullable=True, index=True, comment="원본 텍스트 생성 시간")
    
    # 관계 및 참조
    source_reference = Column(String(100), nullable=True, index=True, comment="원본 데이터 참조 (예: video_id)")
    parent_reference = Column(String(100), nullable=True, index=True, comment="상위 항목 참조 (예: 댓글의 비디오 ID)")
    
    # 추가 데이터
    additional_info = Column(JSONB, nullable=True, comment="추가 메타데이터")
    error = Column(Text, nullable=True, comment="오류 발생 시 메시지")
    
    # 관계 설정
    batch = relationship("SentimentBatch", back_populates="analyses")
    
    # 복합 인덱스 추가 - 시계열 쿼리 및 필터링 최적화
    __table_args__ = (
        Index('ix_sentiment_time_series', source_created_at.desc(), sentiment, text_type),
        Index('ix_sentiment_source_sentiment', source_reference, sentiment),
        Index('ix_sentiment_confidence', confidence.desc()),  # 신뢰도 기반 쿼리 최적화
    )
    
    @validates('sentiment')
    def validate_sentiment(self, key, sentiment):
        """감성 값 검증"""
        allowed_sentiments = ['positive', 'neutral', 'negative']
        if sentiment not in allowed_sentiments:
            raise ValueError(f"Invalid sentiment: {sentiment}. Must be one of {allowed_sentiments}")
        return sentiment


class SentimentAggregate(Base):
    """
    감성 분석 결과의 집계 데이터를 저장하는 모델
    
    일별, 주별, 월별 감성 분석 추세와 통계를 저장합니다.
    대시보드 및 보고서 생성을 위한 최적화된 구조입니다.
    """
    __tablename__ = "sentiment_aggregates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 집계 메타데이터
    aggregate_type = Column(String(20), index=True, nullable=False, comment="집계 타입 (daily, weekly, monthly)")
    date = Column(DateTime, index=True, nullable=False, comment="집계 기준 날짜")
    source = Column(String(50), index=True, nullable=False, comment="데이터 소스")
    source_reference = Column(String(100), nullable=True, index=True, comment="특정 참조 ID (예: 특정 비디오)")
    text_type = Column(String(50), index=True, nullable=False, comment="텍스트 유형")
    
    # 집계 결과
    total_count = Column(Integer, default=0, comment="전체 항목 수")
    positive_count = Column(Integer, default=0, comment="긍정 항목 수")
    neutral_count = Column(Integer, default=0, comment="중립 항목 수")
    negative_count = Column(Integer, default=0, comment="부정 항목 수")
    
    # 비율 및 점수
    positive_ratio = Column(Float, default=0.0, comment="긍정 비율 (0-1)")
    neutral_ratio = Column(Float, default=0.0, comment="중립 비율 (0-1)")
    negative_ratio = Column(Float, default=0.0, comment="부정 비율 (0-1)")
    average_positive_score = Column(Float, default=0.0, comment="평균 긍정 점수")
    average_negative_score = Column(Float, default=0.0, comment="평균 부정 점수")
    sentiment_score = Column(Float, default=0.0, comment="종합 감성 점수 (-1~1, 부정~긍정)")
    
    # 추가 데이터
    top_positive_phrases = Column(JSONB, nullable=True, comment="상위 긍정 문구")
    top_negative_phrases = Column(JSONB, nullable=True, comment="상위 부정 문구")
    additional_info = Column(JSONB, nullable=True, comment="추가 메타데이터")
    
    # 집계 상태
    is_final = Column(Boolean, default=True, comment="최종 집계 여부")
    created_at = Column(DateTime, default=func.now(), comment="집계 생성 시간")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="집계 업데이트 시간")
    
    # 복합 인덱스 추가 - 대시보드 쿼리 최적화
    __table_args__ = (
        # 소스별 시간순 집계 조회
        Index('ix_sentiment_agg_source_date', source, aggregate_type, date.desc()),
        # 참조ID별 시간순 집계 조회
        Index('ix_sentiment_agg_reference_date', source_reference, aggregate_type, date.desc()),
        # 고유성 제약조건
        UniqueConstraint('aggregate_type', 'date', 'source', 'source_reference', 'text_type', name='uq_sentiment_aggregate'),
    )
    
    @validates('aggregate_type')
    def validate_aggregate_type(self, key, aggregate_type):
        """집계 타입 검증"""
        allowed_types = ['daily', 'weekly', 'monthly']
        if aggregate_type not in allowed_types:
            raise ValueError(f"Invalid aggregate_type: {aggregate_type}. Must be one of {allowed_types}")
        return aggregate_type 