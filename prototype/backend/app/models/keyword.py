"""
키워드 추출 결과를 저장하는 데이터베이스 모델

YAKE! 알고리즘으로 추출된 키워드와 카테고리 분류 결과를 PostgreSQL에 효율적으로 저장하기 위한 모델입니다.
시계열 데이터 저장과 카테고리별 분석을 위한 최적화된 인덱스가 포함되어 있습니다.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, Text, Index, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.orm import relationship, validates, DeclarativeBase, mapped_column, Mapped

# SQLAlchemy 2.0 스타일의 기본 클래스 정의
class Base(DeclarativeBase):
    pass


class KeywordBatch(Base):
    """
    키워드 추출 배치 작업 정보를 저장하는 모델
    
    여러 텍스트에 대한 키워드 추출을 일괄 처리할 때 사용되는 배치 정보를 기록합니다.
    각 배치는 여러 개의 KeywordExtraction 인스턴스와 연결됩니다.
    """
    __tablename__ = "keyword_batches"
    
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
    extraction_params = Column(JSONB, nullable=True, comment="키워드 추출 파라미터")
    additional_info = Column(JSONB, nullable=True, comment="추가 메타데이터")
    
    # 관계 설정: 한 배치에 여러 키워드 추출 결과가 연결됨
    extractions = relationship("KeywordExtraction", back_populates="batch", cascade="all, delete-orphan")
    
    # 복합 인덱스 추가 - 쿼리 최적화
    __table_args__ = (
        Index('ix_keyword_batches_source_created', source, created_at.desc()),
        Index('ix_keyword_batches_status_created', status, created_at.desc()),
    )
    
    @validates('status')
    def validate_status(self, key, status):
        """상태 값 검증"""
        allowed_statuses = ['pending', 'processing', 'completed', 'failed']
        if status not in allowed_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {allowed_statuses}")
        return status


class KeywordExtraction(Base):
    """
    개별 텍스트에 대한 키워드 추출 결과를 저장하는 모델
    
    각 텍스트 항목의 키워드 추출 결과 및 관련 메타데이터를 저장합니다.
    카테고리별 키워드 분류 및 시간별 분석을 위한 구조가 포함됩니다.
    """
    __tablename__ = "keyword_extractions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    batch_id = Column(String(36), ForeignKey("keyword_batches.batch_id"), index=True, nullable=False, comment="연결된 배치 ID")
    text_id = Column(String(100), index=True, nullable=False, comment="분석된 텍스트의 고유 ID (예: 댓글 ID)")
    text_type = Column(String(50), index=True, nullable=False, comment="텍스트 유형 (예: comment, review, post)")
    original_text = Column(Text, nullable=True, comment="원본 텍스트")
    processed_text = Column(Text, nullable=True, comment="전처리된 텍스트")
    
    # 키워드 추출 결과
    keywords = Column(JSONB, nullable=False, comment="추출된 키워드 목록 [{keyword, score, category}, ...]")
    top_keywords = Column(ARRAY(String), nullable=True, comment="상위 키워드 목록 (배열)")
    
    # 카테고리별 키워드
    taste_keywords = Column(JSONB, nullable=True, comment="맛 관련 키워드")
    price_keywords = Column(JSONB, nullable=True, comment="가격 관련 키워드")
    packaging_keywords = Column(JSONB, nullable=True, comment="패키징 관련 키워드")
    place_keywords = Column(JSONB, nullable=True, comment="판매처 관련 키워드")
    repurchase_keywords = Column(JSONB, nullable=True, comment="재구매 의향 관련 키워드")
    other_keywords = Column(JSONB, nullable=True, comment="기타 키워드")
    
    # 시간 관련 필드
    extracted_at = Column(DateTime, default=func.now(), index=True, comment="추출 시간")
    source_created_at = Column(DateTime, nullable=True, index=True, comment="원본 텍스트 생성 시간")
    
    # 관계 및 참조
    source_reference = Column(String(100), nullable=True, index=True, comment="원본 데이터 참조 (예: video_id)")
    parent_reference = Column(String(100), nullable=True, index=True, comment="상위 항목 참조 (예: 댓글의 비디오 ID)")
    
    # 추가 데이터
    dominant_category = Column(String(50), index=True, nullable=True, comment="주요 카테고리 (가장 많은 키워드가 속한 카테고리)")
    sentiment_hint = Column(String(20), index=True, nullable=True, comment="키워드 기반 감성 힌트 (positive, neutral, negative)")
    additional_info = Column(JSONB, nullable=True, comment="추가 메타데이터")
    error = Column(Text, nullable=True, comment="오류 발생 시 메시지")
    
    # 관계 설정
    batch = relationship("KeywordBatch", back_populates="extractions")
    
    # 복합 인덱스 추가 - 시계열 쿼리 및 필터링 최적화
    __table_args__ = (
        # 시간 기반 쿼리 최적화
        Index('ix_keyword_time_series', source_created_at.desc(), text_type),
        # 소스 참조별 쿼리 최적화
        Index('ix_keyword_source_category', source_reference, dominant_category),
        # 텍스트 ID와 유형에 대한 고유 제약
        UniqueConstraint('text_id', 'text_type', name='uq_keyword_text_id_type'),
    )


class KeywordAggregate(Base):
    """
    키워드 추출 결과의 집계 데이터를 저장하는 모델
    
    일별, 주별, 월별 키워드 추출 추세와 통계를 저장합니다.
    대시보드 및 인사이트 생성을 위한 최적화된 구조입니다.
    """
    __tablename__ = "keyword_aggregates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # 집계 메타데이터
    aggregate_type = Column(String(20), index=True, nullable=False, comment="집계 타입 (daily, weekly, monthly)")
    date = Column(DateTime, index=True, nullable=False, comment="집계 기준 날짜")
    source = Column(String(50), index=True, nullable=False, comment="데이터 소스")
    source_reference = Column(String(100), nullable=True, index=True, comment="특정 참조 ID (예: 특정 비디오)")
    text_type = Column(String(50), index=True, nullable=False, comment="텍스트 유형")
    category = Column(String(50), index=True, nullable=True, comment="카테고리 (없으면 전체)")
    
    # 집계 결과
    total_count = Column(Integer, default=0, comment="전체 항목 수")
    
    # 카테고리별 키워드 수
    taste_count = Column(Integer, default=0, comment="맛 관련 키워드 수")
    price_count = Column(Integer, default=0, comment="가격 관련 키워드 수")
    packaging_count = Column(Integer, default=0, comment="패키징 관련 키워드 수")
    place_count = Column(Integer, default=0, comment="판매처 관련 키워드 수")
    repurchase_count = Column(Integer, default=0, comment="재구매 의향 관련 키워드 수")
    other_count = Column(Integer, default=0, comment="기타 키워드 수")
    
    # 카테고리별 비율
    taste_ratio = Column(Float, default=0.0, comment="맛 관련 키워드 비율 (0-1)")
    price_ratio = Column(Float, default=0.0, comment="가격 관련 키워드 비율 (0-1)")
    packaging_ratio = Column(Float, default=0.0, comment="패키징 관련 키워드 비율 (0-1)")
    place_ratio = Column(Float, default=0.0, comment="판매처 관련 키워드 비율 (0-1)")
    repurchase_ratio = Column(Float, default=0.0, comment="재구매 의향 관련 키워드 비율 (0-1)")
    other_ratio = Column(Float, default=0.0, comment="기타 키워드 비율 (0-1)")
    
    # 상위 키워드
    top_keywords = Column(JSONB, nullable=True, comment="전체 상위 키워드 {keyword: count, ...}")
    top_keywords_by_category = Column(JSONB, nullable=True, comment="카테고리별 상위 키워드 {category: {keyword: count, ...}, ...}")
    
    # 키워드 트렌드
    trending_keywords = Column(JSONB, nullable=True, comment="상승세 키워드 {keyword: growth_rate, ...}")
    declining_keywords = Column(JSONB, nullable=True, comment="하강세 키워드 {keyword: decline_rate, ...}")
    
    # 추가 데이터
    keyword_associations = Column(JSONB, nullable=True, comment="키워드 연관성 {keyword: [associated_keywords], ...}")
    additional_info = Column(JSONB, nullable=True, comment="추가 메타데이터")
    
    # 집계 상태
    is_final = Column(Boolean, default=True, comment="최종 집계 여부")
    created_at = Column(DateTime, default=func.now(), comment="집계 생성 시간")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), comment="집계 업데이트 시간")
    
    # 복합 인덱스 추가 - 대시보드 쿼리 최적화
    __table_args__ = (
        # 소스별 시간순 집계 조회
        Index('ix_keyword_agg_source_date', source, aggregate_type, date.desc()),
        # 참조ID별 시간순 집계 조회
        Index('ix_keyword_agg_reference_date', source_reference, aggregate_type, date.desc()),
        # 카테고리별 시간순 집계 조회
        Index('ix_keyword_agg_category_date', category, aggregate_type, date.desc()),
        # 고유성 제약조건
        UniqueConstraint('aggregate_type', 'date', 'source', 'source_reference', 'text_type', 'category', name='uq_keyword_aggregate'),
    )
    
    @validates('aggregate_type')
    def validate_aggregate_type(self, key, aggregate_type):
        """집계 타입 검증"""
        allowed_types = ['daily', 'weekly', 'monthly']
        if aggregate_type not in allowed_types:
            raise ValueError(f"Invalid aggregate_type: {aggregate_type}. Must be one of {allowed_types}")
        return aggregate_type
    
    @validates('category')
    def validate_category(self, key, category):
        """카테고리 검증"""
        if category is not None:
            allowed_categories = ['taste', 'price', 'packaging', 'place', 'repurchase', 'other', 'all']
            if category not in allowed_categories:
                raise ValueError(f"Invalid category: {category}. Must be one of {allowed_categories}")
        return category 