"""
분석 결과 API 엔드포인트

감성 분석 및 키워드 추출 결과를 조회하는 엔드포인트를 제공합니다.
시간 범위 및 제품 카테고리별 필터링이 가능합니다.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.sentiment import SentimentAnalysis, SentimentAggregate
from app.models.keyword import KeywordExtraction, KeywordAggregate
from app.models.youtube_data import YouTubeVideo, YouTubeComment


# 라우터 정의
router = APIRouter()


# 응답 모델 정의
class SentimentResponse(BaseModel):
    id: int
    source_id: int
    source_type: str
    text_preview: str
    sentiment: str
    positive: float
    negative: float
    neutral: float
    confidence: float
    created_at: datetime
    
    class Config:
        orm_mode = True


class KeywordResponse(BaseModel):
    id: int
    source_id: int
    source_type: str
    text_preview: str
    keywords: List[Dict[str, Any]]
    categories: Dict[str, List[str]]
    created_at: datetime
    
    class Config:
        orm_mode = True


class SentimentAggregateResponse(BaseModel):
    time_period: str
    positive_count: int
    negative_count: int
    neutral_count: int
    total_count: int
    positive_ratio: float
    negative_ratio: float
    neutral_ratio: float
    
    class Config:
        orm_mode = True


class KeywordAggregateResponse(BaseModel):
    time_period: str
    category: str
    keywords: List[Dict[str, Any]]
    count: int
    
    class Config:
        orm_mode = True


class AnalysisOverviewResponse(BaseModel):
    total_analyzed: int
    sentiment_distribution: Dict[str, float]
    top_categories: List[Dict[str, Any]]
    top_keywords: List[Dict[str, Any]]
    recent_positive_keywords: List[str]
    recent_negative_keywords: List[str]
    
    class Config:
        orm_mode = True


# API 엔드포인트 구현
@router.get("/sentiment", response_model=List[SentimentResponse])
async def get_sentiment_analysis(
    start_date: Optional[datetime] = Query(None, description="시작 날짜 (ISO 형식)"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜 (ISO 형식)"),
    category: Optional[str] = Query(None, description="제품 카테고리"),
    sentiment: Optional[str] = Query(None, description="감성 분류 (positive, neutral, negative)"),
    limit: int = Query(100, description="결과 제한 수"),
    offset: int = Query(0, description="결과 오프셋"),
    db: AsyncSession = Depends(get_db)
):
    """
    감성 분석 결과를 조회합니다.
    
    - 시간 범위, 카테고리, 감성 분류별 필터링이 가능합니다.
    - 페이지네이션을 지원합니다.
    """
    # 기본 쿼리 설정
    query = select(SentimentAnalysis)
    
    # 필터 적용
    filters = []
    
    # 날짜 필터
    if start_date:
        filters.append(SentimentAnalysis.created_at >= start_date)
    if end_date:
        filters.append(SentimentAnalysis.created_at <= end_date)
    
    # 감성 필터
    if sentiment:
        filters.append(SentimentAnalysis.sentiment == sentiment)
    
    # 카테고리 필터 (유튜브 비디오 관련)
    if category:
        # YouTube 비디오일 경우 카테고리 필터 적용
        subquery = (
            select(YouTubeVideo.id)
            .where(YouTubeVideo.categories.contains([category]))
        )
        
        filters.append(
            and_(
                SentimentAnalysis.source_type == "youtube_video",
                SentimentAnalysis.source_id.in_(subquery)
            )
        )
    
    # 필터 적용
    if filters:
        query = query.where(and_(*filters))
    
    # 정렬 및 페이지네이션
    query = query.order_by(SentimentAnalysis.created_at.desc())
    query = query.offset(offset).limit(limit)
    
    # 결과 조회
    result = await db.execute(query)
    sentiment_analyses = result.scalars().all()
    
    return sentiment_analyses


@router.get("/sentiment/aggregate", response_model=List[SentimentAggregateResponse])
async def get_sentiment_aggregate(
    period: str = Query("day", description="집계 기간 (hour, day, week, month)"),
    start_date: Optional[datetime] = Query(None, description="시작 날짜 (ISO 형식)"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜 (ISO 형식)"),
    category: Optional[str] = Query(None, description="제품 카테고리"),
    db: AsyncSession = Depends(get_db)
):
    """
    감성 분석 결과의 시계열 집계 데이터를 조회합니다.
    
    - 시간별, 일별, 주별, 월별 집계를 지원합니다.
    - 카테고리별 필터링이 가능합니다.
    """
    # 기본 쿼리 설정
    query = select(SentimentAggregate)
    
    # 필터 적용
    filters = []
    
    # 집계 기간 필터
    filters.append(SentimentAggregate.period_type == period)
    
    # 날짜 필터
    if start_date:
        filters.append(SentimentAggregate.period_start >= start_date)
    if end_date:
        filters.append(SentimentAggregate.period_end <= end_date)
    
    # 카테고리 필터
    if category:
        filters.append(SentimentAggregate.category == category)
    
    # 필터 적용
    if filters:
        query = query.where(and_(*filters))
    
    # 정렬
    query = query.order_by(SentimentAggregate.period_start.desc())
    
    # 결과 조회
    result = await db.execute(query)
    aggregates = result.scalars().all()
    
    return aggregates


@router.get("/keywords", response_model=List[KeywordResponse])
async def get_keyword_extractions(
    start_date: Optional[datetime] = Query(None, description="시작 날짜 (ISO 형식)"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜 (ISO 형식)"),
    category: Optional[str] = Query(None, description="제품 카테고리 (taste, price, packaging, place, repurchase)"),
    keyword: Optional[str] = Query(None, description="특정 키워드 검색"),
    limit: int = Query(100, description="결과 제한 수"),
    offset: int = Query(0, description="결과 오프셋"),
    db: AsyncSession = Depends(get_db)
):
    """
    키워드 추출 결과를 조회합니다.
    
    - 시간 범위, 카테고리별 필터링이 가능합니다.
    - 특정 키워드를 검색할 수 있습니다.
    - 페이지네이션을 지원합니다.
    """
    # 기본 쿼리 설정
    query = select(KeywordExtraction)
    
    # 필터 적용
    filters = []
    
    # 날짜 필터
    if start_date:
        filters.append(KeywordExtraction.created_at >= start_date)
    if end_date:
        filters.append(KeywordExtraction.created_at <= end_date)
    
    # 카테고리 필터
    if category:
        # 카테고리별 키워드 필터링
        # JSON 필드에서 카테고리 키를 검색하는 필터
        filters.append(
            KeywordExtraction.categories.has_key(category)
        )
    
    # 키워드 검색
    if keyword:
        # JSON 배열에 특정 키워드가 포함된 레코드 검색
        filters.append(
            KeywordExtraction.keywords.contains([{"keyword": keyword}])
        )
    
    # 필터 적용
    if filters:
        query = query.where(and_(*filters))
    
    # 정렬 및 페이지네이션
    query = query.order_by(KeywordExtraction.created_at.desc())
    query = query.offset(offset).limit(limit)
    
    # 결과 조회
    result = await db.execute(query)
    keyword_extractions = result.scalars().all()
    
    return keyword_extractions


@router.get("/keywords/aggregate", response_model=List[KeywordAggregateResponse])
async def get_keyword_aggregate(
    period: str = Query("day", description="집계 기간 (hour, day, week, month)"),
    category: str = Query(..., description="키워드 카테고리 (taste, price, packaging, place, repurchase)"),
    start_date: Optional[datetime] = Query(None, description="시작 날짜 (ISO 형식)"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜 (ISO 형식)"),
    limit: int = Query(20, description="결과 제한 수"),
    db: AsyncSession = Depends(get_db)
):
    """
    키워드 추출 결과의 시계열 집계 데이터를 조회합니다.
    
    - 시간별, 일별, 주별, 월별 집계를 지원합니다.
    - 카테고리별 필터링이 가능합니다.
    """
    # 기본 쿼리 설정
    query = select(KeywordAggregate)
    
    # 필터 적용
    filters = []
    
    # 집계 기간 필터
    filters.append(KeywordAggregate.period_type == period)
    
    # 카테고리 필터
    filters.append(KeywordAggregate.category == category)
    
    # 날짜 필터
    if start_date:
        filters.append(KeywordAggregate.period_start >= start_date)
    if end_date:
        filters.append(KeywordAggregate.period_end <= end_date)
    
    # 필터 적용
    if filters:
        query = query.where(and_(*filters))
    
    # 정렬
    query = query.order_by(KeywordAggregate.period_start.desc())
    query = query.limit(limit)
    
    # 결과 조회
    result = await db.execute(query)
    aggregates = result.scalars().all()
    
    return aggregates


@router.get("/overview", response_model=AnalysisOverviewResponse)
async def get_analysis_overview(
    days: int = Query(30, description="최근 기간 (일 단위)"),
    db: AsyncSession = Depends(get_db)
):
    """
    분석 결과의 전체 개요를 조회합니다.
    
    - 전체 분석된 항목 수
    - 감성 분포
    - 상위 카테고리
    - 상위 키워드
    - 최근 긍정/부정 키워드
    """
    # 기준 날짜 설정 (현재로부터 N일 전)
    reference_date = datetime.utcnow() - timedelta(days=days)
    
    # 전체 분석된 항목 수
    sentiment_count_query = select(func.count()).select_from(SentimentAnalysis)
    sentiment_count_result = await db.execute(sentiment_count_query)
    total_analyzed = sentiment_count_result.scalar()
    
    # 감성 분포
    sentiment_distribution_query = (
        select(
            SentimentAnalysis.sentiment,
            func.count().label("count")
        )
        .where(SentimentAnalysis.created_at >= reference_date)
        .group_by(SentimentAnalysis.sentiment)
    )
    sentiment_distribution_result = await db.execute(sentiment_distribution_query)
    sentiment_counts = {row[0]: row[1] for row in sentiment_distribution_result.all()}
    
    total = sum(sentiment_counts.values()) or 1  # 0으로 나누기 방지
    sentiment_distribution = {
        sentiment: count / total
        for sentiment, count in sentiment_counts.items()
    }
    
    # 상위 카테고리
    top_categories_query = (
        select(
            KeywordAggregate.category,
            func.sum(KeywordAggregate.count).label("total_count")
        )
        .where(KeywordAggregate.period_start >= reference_date)
        .group_by(KeywordAggregate.category)
        .order_by(func.sum(KeywordAggregate.count).desc())
        .limit(5)
    )
    top_categories_result = await db.execute(top_categories_query)
    top_categories = [
        {"category": row[0], "count": row[1]}
        for row in top_categories_result.all()
    ]
    
    # 상위 키워드
    # 복잡한 JSON 집계를 위한 원시 SQL 쿼리 사용
    # PostgreSQL의 jsonb_array_elements 함수 활용
    top_keywords_result = await db.execute(
        """
        WITH keyword_elements AS (
            SELECT 
                jsonb_array_elements(keywords) as keyword_object
            FROM 
                keyword_extraction
            WHERE 
                created_at >= :reference_date
        )
        SELECT 
            keyword_object->>'keyword' as keyword,
            COUNT(*) as count
        FROM 
            keyword_elements
        GROUP BY 
            keyword
        ORDER BY 
            count DESC
        LIMIT 20
        """,
        {"reference_date": reference_date}
    )
    top_keywords = [
        {"keyword": row[0], "count": row[1]}
        for row in top_keywords_result.all()
    ]
    
    # 최근 긍정 키워드
    recent_positive_query = (
        select(KeywordExtraction.categories["taste"].label("taste_keywords"))
        .join(
            SentimentAnalysis,
            and_(
                KeywordExtraction.source_id == SentimentAnalysis.source_id,
                KeywordExtraction.source_type == SentimentAnalysis.source_type
            )
        )
        .where(
            and_(
                SentimentAnalysis.sentiment == "positive",
                SentimentAnalysis.created_at >= reference_date
            )
        )
        .order_by(SentimentAnalysis.created_at.desc())
        .limit(10)
    )
    recent_positive_result = await db.execute(recent_positive_query)
    
    # 키워드 목록 병합 및 중복 제거
    recent_positive_keywords = []
    for row in recent_positive_result.all():
        if row[0] and isinstance(row[0], list):
            recent_positive_keywords.extend(row[0])
    
    recent_positive_keywords = list(set(recent_positive_keywords))[:10]
    
    # 최근 부정 키워드
    recent_negative_query = (
        select(KeywordExtraction.categories["taste"].label("taste_keywords"))
        .join(
            SentimentAnalysis,
            and_(
                KeywordExtraction.source_id == SentimentAnalysis.source_id,
                KeywordExtraction.source_type == SentimentAnalysis.source_type
            )
        )
        .where(
            and_(
                SentimentAnalysis.sentiment == "negative",
                SentimentAnalysis.created_at >= reference_date
            )
        )
        .order_by(SentimentAnalysis.created_at.desc())
        .limit(10)
    )
    recent_negative_result = await db.execute(recent_negative_query)
    
    # 키워드 목록 병합 및 중복 제거
    recent_negative_keywords = []
    for row in recent_negative_result.all():
        if row[0] and isinstance(row[0], list):
            recent_negative_keywords.extend(row[0])
    
    recent_negative_keywords = list(set(recent_negative_keywords))[:10]
    
    # 응답 구성
    return {
        "total_analyzed": total_analyzed,
        "sentiment_distribution": sentiment_distribution,
        "top_categories": top_categories,
        "top_keywords": top_keywords,
        "recent_positive_keywords": recent_positive_keywords,
        "recent_negative_keywords": recent_negative_keywords
    }


@router.get("/trends/sentiment", response_model=List[Dict[str, Any]])
async def get_sentiment_trends(
    period: str = Query("day", description="집계 기간 (hour, day, week, month)"),
    start_date: Optional[datetime] = Query(None, description="시작 날짜 (ISO 형식)"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜 (ISO 형식)"),
    db: AsyncSession = Depends(get_db)
):
    """
    감성 분석 결과의 시간에 따른 트렌드 데이터를 조회합니다.
    
    - 시간별, 일별, 주별, 월별 집계를 지원합니다.
    - 각 시간 구간별 긍정/중립/부정 비율을 반환합니다.
    """
    # 기본 쿼리 설정
    query = select(SentimentAggregate)
    
    # 필터 적용
    filters = []
    
    # 집계 기간 필터
    filters.append(SentimentAggregate.period_type == period)
    
    # 날짜 필터
    if start_date:
        filters.append(SentimentAggregate.period_start >= start_date)
    if end_date:
        filters.append(SentimentAggregate.period_end <= end_date)
    
    # 필터 적용
    if filters:
        query = query.where(and_(*filters))
    
    # 결과 정렬
    query = query.order_by(SentimentAggregate.period_start)
    
    # 결과 조회
    result = await db.execute(query)
    aggregates = result.scalars().all()
    
    # 트렌드 데이터 구성
    trends = []
    for aggregate in aggregates:
        total = aggregate.positive_count + aggregate.negative_count + aggregate.neutral_count
        if total > 0:
            trends.append({
                "period": aggregate.period_start.isoformat(),
                "positive_ratio": aggregate.positive_count / total,
                "neutral_ratio": aggregate.neutral_count / total,
                "negative_ratio": aggregate.negative_count / total,
                "total_count": total
            })
    
    return trends


@router.get("/trends/keywords", response_model=List[Dict[str, Any]])
async def get_keyword_trends(
    category: str = Query(..., description="키워드 카테고리 (taste, price, packaging, place, repurchase)"),
    period: str = Query("day", description="집계 기간 (hour, day, week, month)"),
    top_n: int = Query(5, description="각 기간별 상위 키워드 수"),
    start_date: Optional[datetime] = Query(None, description="시작 날짜 (ISO 형식)"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜 (ISO 형식)"),
    db: AsyncSession = Depends(get_db)
):
    """
    키워드 추출 결과의 시간에 따른 트렌드 데이터를 조회합니다.
    
    - 시간별, 일별, 주별, 월별 집계를 지원합니다.
    - 각 시간 구간별 상위 키워드를 반환합니다.
    """
    # 기본 쿼리 설정
    query = select(KeywordAggregate)
    
    # 필터 적용
    filters = []
    
    # 집계 기간 필터
    filters.append(KeywordAggregate.period_type == period)
    
    # 카테고리 필터
    filters.append(KeywordAggregate.category == category)
    
    # 날짜 필터
    if start_date:
        filters.append(KeywordAggregate.period_start >= start_date)
    if end_date:
        filters.append(KeywordAggregate.period_end <= end_date)
    
    # 필터 적용
    if filters:
        query = query.where(and_(*filters))
    
    # 결과 정렬
    query = query.order_by(KeywordAggregate.period_start)
    
    # 결과 조회
    result = await db.execute(query)
    aggregates = result.scalars().all()
    
    # 트렌드 데이터 구성
    trends = []
    for aggregate in aggregates:
        # 키워드 정렬 및 상위 N개 선택
        sorted_keywords = sorted(
            aggregate.keywords, 
            key=lambda k: k.get("count", 0), 
            reverse=True
        )[:top_n]
        
        trends.append({
            "period": aggregate.period_start.isoformat(),
            "category": aggregate.category,
            "keywords": sorted_keywords,
            "total_count": aggregate.count
        })
    
    return trends 