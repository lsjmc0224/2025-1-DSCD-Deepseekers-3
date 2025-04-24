"""
YouTube 데이터 CRUD 작업

이 모듈은 YouTube 관련 모델에 대한 데이터베이스 CRUD 작업을 제공합니다.
CREATE, READ, UPDATE, DELETE 작업을 비동기적으로 수행합니다.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any, Union

from sqlalchemy import and_, or_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.youtube_data import YouTubeVideo, YouTubeComment, YouTubeSentimentAnalysis, CollectionJob


async def create_youtube_video(
    db: AsyncSession, 
    video_data: Dict[str, Any]
) -> YouTubeVideo:
    """
    새 YouTube 동영상 정보를 생성합니다.
    
    Args:
        db: 비동기 데이터베이스 세션
        video_data: 동영상 데이터 딕셔너리
        
    Returns:
        생성된 YouTubeVideo 모델 인스턴스
    """
    # 필수 필드 확인
    required_fields = ["youtube_id", "title", "channel_id", "channel_title", "published_at"]
    for field in required_fields:
        if field not in video_data:
            raise ValueError(f"필수 필드가 누락되었습니다: {field}")
    
    # 기존 동영상 확인
    result = await db.execute(
        select(YouTubeVideo).where(YouTubeVideo.youtube_id == video_data["youtube_id"])
    )
    existing_video = result.scalars().first()
    
    if existing_video:
        # 기존 동영상 업데이트
        for key, value in video_data.items():
            if hasattr(existing_video, key) and key != "id":
                setattr(existing_video, key, value)
        
        existing_video.last_fetched_at = datetime.utcnow()
        await db.commit()
        await db.refresh(existing_video)
        return existing_video
    
    # 새 동영상 생성
    video = YouTubeVideo(**video_data)
    db.add(video)
    await db.commit()
    await db.refresh(video)
    return video


async def get_youtube_video(
    db: AsyncSession, 
    youtube_id: str
) -> Optional[YouTubeVideo]:
    """
    YouTube ID로 동영상 정보를 조회합니다.
    
    Args:
        db: 비동기 데이터베이스 세션
        youtube_id: YouTube 동영상 ID
        
    Returns:
        조회된 YouTubeVideo 모델 또는 None
    """
    result = await db.execute(
        select(YouTubeVideo).where(YouTubeVideo.youtube_id == youtube_id)
    )
    return result.scalars().first()


async def get_youtube_videos(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    channel_id: Optional[str] = None,
    keyword: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    order_by: str = "published_at",
    desc_order: bool = True
) -> Tuple[List[YouTubeVideo], int]:
    """
    YouTube 동영상 목록을 조회합니다.
    
    Args:
        db: 비동기 데이터베이스 세션
        skip: 건너뛸 레코드 수
        limit: 반환할 최대 레코드 수
        channel_id: 채널 ID 필터
        keyword: 제목 또는 설명 검색어
        start_date: 시작 날짜 필터
        end_date: 종료 날짜 필터
        order_by: 정렬 기준 컬럼
        desc_order: 내림차순 정렬 여부
        
    Returns:
        (동영상 목록, 총 개수) 튜플
    """
    # 기본 쿼리
    query = select(YouTubeVideo)
    count_query = select(func.count(YouTubeVideo.id))
    
    # 필터 적용
    filters = []
    
    if channel_id:
        filters.append(YouTubeVideo.channel_id == channel_id)
    
    if keyword:
        filters.append(
            or_(
                YouTubeVideo.title.ilike(f"%{keyword}%"),
                YouTubeVideo.description.ilike(f"%{keyword}%")
            )
        )
    
    if start_date:
        filters.append(YouTubeVideo.published_at >= start_date)
    
    if end_date:
        filters.append(YouTubeVideo.published_at <= end_date)
    
    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))
    
    # 정렬 적용
    if hasattr(YouTubeVideo, order_by):
        order_col = getattr(YouTubeVideo, order_by)
        query = query.order_by(desc(order_col) if desc_order else order_col)
    else:
        query = query.order_by(desc(YouTubeVideo.published_at) if desc_order else YouTubeVideo.published_at)
    
    # 페이징 적용
    query = query.offset(skip).limit(limit)
    
    # 쿼리 실행
    result = await db.execute(query)
    count_result = await db.execute(count_query)
    
    return result.scalars().all(), count_result.scalar()


async def create_youtube_comment(
    db: AsyncSession, 
    comment_data: Dict[str, Any]
) -> YouTubeComment:
    """
    새 YouTube 댓글을 생성합니다.
    
    Args:
        db: 비동기 데이터베이스 세션
        comment_data: 댓글 데이터 딕셔너리
        
    Returns:
        생성된 YouTubeComment 모델 인스턴스
    """
    # 필수 필드 확인
    required_fields = ["video_id", "comment_id", "text", "author_name", "published_at"]
    for field in required_fields:
        if field not in comment_data:
            raise ValueError(f"필수 필드가 누락되었습니다: {field}")
    
    # 기존 댓글 확인
    result = await db.execute(
        select(YouTubeComment).where(YouTubeComment.comment_id == comment_data["comment_id"])
    )
    existing_comment = result.scalars().first()
    
    if existing_comment:
        # 기존 댓글 업데이트
        for key, value in comment_data.items():
            if hasattr(existing_comment, key) and key != "id":
                setattr(existing_comment, key, value)
        
        await db.commit()
        await db.refresh(existing_comment)
        return existing_comment
    
    # 새 댓글 생성
    comment = YouTubeComment(**comment_data)
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


async def get_youtube_comments(
    db: AsyncSession,
    video_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    sentiment: Optional[str] = None,
    order_by: str = "published_at",
    desc_order: bool = True
) -> Tuple[List[YouTubeComment], int]:
    """
    YouTube 댓글 목록을 조회합니다.
    
    Args:
        db: 비동기 데이터베이스 세션
        video_id: 비디오 ID 필터
        skip: 건너뛸 레코드 수
        limit: 반환할 최대 레코드 수
        sentiment: 감성 레이블 필터
        order_by: 정렬 기준 컬럼
        desc_order: 내림차순 정렬 여부
        
    Returns:
        (댓글 목록, 총 개수) 튜플
    """
    # 기본 쿼리
    query = select(YouTubeComment)
    count_query = select(func.count(YouTubeComment.id))
    
    # 필터 적용
    filters = []
    
    if video_id:
        filters.append(YouTubeComment.video_id == video_id)
    
    if sentiment:
        filters.append(YouTubeComment.sentiment_label == sentiment)
    
    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))
    
    # 정렬 적용
    if hasattr(YouTubeComment, order_by):
        order_col = getattr(YouTubeComment, order_by)
        query = query.order_by(desc(order_col) if desc_order else order_col)
    else:
        query = query.order_by(desc(YouTubeComment.published_at) if desc_order else YouTubeComment.published_at)
    
    # 페이징 적용
    query = query.offset(skip).limit(limit)
    
    # 쿼리 실행
    result = await db.execute(query)
    count_result = await db.execute(count_query)
    
    return result.scalars().all(), count_result.scalar()


async def create_sentiment_analysis(
    db: AsyncSession, 
    analysis_data: Dict[str, Any]
) -> YouTubeSentimentAnalysis:
    """
    새 YouTube 감성 분석 결과를 생성합니다.
    
    Args:
        db: 비동기 데이터베이스 세션
        analysis_data: 감성 분석 데이터 딕셔너리
        
    Returns:
        생성된 YouTubeSentimentAnalysis 모델 인스턴스
    """
    # 필수 필드 확인
    required_fields = ["video_id", "positive_count", "negative_count", "neutral_count"]
    for field in required_fields:
        if field not in analysis_data:
            raise ValueError(f"필수 필드가 누락되었습니다: {field}")
    
    # 기존 분석 결과 확인
    result = await db.execute(
        select(YouTubeSentimentAnalysis).where(YouTubeSentimentAnalysis.video_id == analysis_data["video_id"])
    )
    existing_analysis = result.scalars().first()
    
    if existing_analysis:
        # 기존 분석 결과 업데이트
        for key, value in analysis_data.items():
            if hasattr(existing_analysis, key) and key != "id":
                setattr(existing_analysis, key, value)
        
        existing_analysis.analyzed_at = datetime.utcnow()
        await db.commit()
        await db.refresh(existing_analysis)
        return existing_analysis
    
    # 새 분석 결과 생성
    analysis = YouTubeSentimentAnalysis(**analysis_data)
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return analysis


async def get_sentiment_analysis(
    db: AsyncSession, 
    video_id: str
) -> Optional[YouTubeSentimentAnalysis]:
    """
    비디오 ID로 감성 분석 결과를 조회합니다.
    
    Args:
        db: 비동기 데이터베이스 세션
        video_id: 비디오 ID
        
    Returns:
        조회된 YouTubeSentimentAnalysis 모델 또는 None
    """
    result = await db.execute(
        select(YouTubeSentimentAnalysis).where(YouTubeSentimentAnalysis.video_id == video_id)
    )
    return result.scalars().first()


async def create_collection_job(
    db: AsyncSession, 
    job_data: Dict[str, Any]
) -> CollectionJob:
    """
    새 데이터 수집 작업을 생성합니다.
    
    Args:
        db: 비동기 데이터베이스 세션
        job_data: 작업 데이터 딕셔너리
        
    Returns:
        생성된 CollectionJob 모델 인스턴스
    """
    # 필수 필드 확인
    required_fields = ["type", "status"]
    for field in required_fields:
        if field not in job_data:
            raise ValueError(f"필수 필드가 누락되었습니다: {field}")
    
    # 새 작업 생성
    job = CollectionJob(**job_data)
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def update_collection_job(
    db: AsyncSession, 
    job_id: str, 
    job_data: Dict[str, Any]
) -> Optional[CollectionJob]:
    """
    데이터 수집 작업을 업데이트합니다.
    
    Args:
        db: 비동기 데이터베이스 세션
        job_id: 작업 ID
        job_data: 업데이트할 작업 데이터 딕셔너리
        
    Returns:
        업데이트된 CollectionJob 모델 또는 None
    """
    result = await db.execute(
        select(CollectionJob).where(CollectionJob.id == job_id)
    )
    job = result.scalars().first()
    
    if not job:
        return None
    
    for key, value in job_data.items():
        if hasattr(job, key) and key != "id":
            setattr(job, key, value)
    
    if job_data.get("status") in ["completed", "failed"]:
        job.completed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(job)
    return job


async def get_collection_job(
    db: AsyncSession, 
    job_id: str
) -> Optional[CollectionJob]:
    """
    작업 ID로 수집 작업을 조회합니다.
    
    Args:
        db: 비동기 데이터베이스 세션
        job_id: 작업 ID
        
    Returns:
        조회된 CollectionJob 모델 또는 None
    """
    result = await db.execute(
        select(CollectionJob).where(CollectionJob.id == job_id)
    )
    return result.scalars().first()


async def get_collection_jobs(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    job_type: Optional[str] = None,
    status: Optional[str] = None
) -> Tuple[List[CollectionJob], int]:
    """
    데이터 수집 작업 목록을 조회합니다.
    
    Args:
        db: 비동기 데이터베이스 세션
        skip: 건너뛸 레코드 수
        limit: 반환할 최대 레코드 수
        job_type: 작업 유형 필터
        status: 상태 필터
        
    Returns:
        (작업 목록, 총 개수) 튜플
    """
    # 기본 쿼리
    query = select(CollectionJob).order_by(desc(CollectionJob.started_at))
    count_query = select(func.count(CollectionJob.id))
    
    # 필터 적용
    filters = []
    
    if job_type:
        filters.append(CollectionJob.type == job_type)
    
    if status:
        filters.append(CollectionJob.status == status)
    
    if filters:
        query = query.where(and_(*filters))
        count_query = count_query.where(and_(*filters))
    
    # 페이징 적용
    query = query.offset(skip).limit(limit)
    
    # 쿼리 실행
    result = await db.execute(query)
    count_result = await db.execute(count_query)
    
    return result.scalars().all(), count_result.scalar() 