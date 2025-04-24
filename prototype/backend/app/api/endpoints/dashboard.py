"""
대시보드 API 엔드포인트

이 모듈은 대시보드를 위한 API 엔드포인트를 제공합니다.
분석 결과 통계, 최근 수집 데이터, 감성 분석 결과 등을 제공합니다.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, HTTPException, Path, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, desc
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.youtube_data import YouTubeVideo, YouTubeComment, YouTubeSentimentAnalysis
from app.crud import youtube as crud_youtube

# 라우터 정의
router = APIRouter()

# 응답 모델 정의
class SentimentDistribution(BaseModel):
    positive: float = Field(..., description="긍정 댓글 비율 (0-1)", example=0.65)
    negative: float = Field(..., description="부정 댓글 비율 (0-1)", example=0.15)
    neutral: float = Field(..., description="중립 댓글 비율 (0-1)", example=0.2)

class CollectionJobInfo(BaseModel):
    id: str = Field(..., description="작업 ID")
    type: str = Field(..., description="작업 유형", example="youtube_collection")
    status: str = Field(..., description="작업 상태", example="completed")
    progress: float = Field(..., description="작업 진행률 (0-100)", example=100.0)
    started_at: Optional[datetime] = Field(None, description="작업 시작 시간")
    completed_at: Optional[datetime] = Field(None, description="작업 완료 시간")

class DashboardSummary(BaseModel):
    totalVideos: int = Field(..., description="총 수집된 비디오 수", example=120)
    totalComments: int = Field(..., description="총 수집된 댓글 수", example=3500)
    recentVideos: int = Field(..., description="최근 7일간 수집된 비디오 수", example=25)
    averageSentiment: float = Field(..., description="평균 감성 점수", example=0.35)
    sentimentDistribution: SentimentDistribution
    recentJobs: List[CollectionJobInfo]
    lastUpdated: datetime = Field(..., description="마지막 업데이트 시간")

class SentimentAnalysisResult(BaseModel):
    positivePercentage: float = Field(..., description="긍정 댓글 비율 (%)", example=65.0)
    negativePercentage: float = Field(..., description="부정 댓글 비율 (%)", example=15.0)
    neutralPercentage: float = Field(..., description="중립 댓글 비율 (%)", example=20.0)
    averageScore: float = Field(..., description="평균 감성 점수 (-1 ~ 1)", example=0.35)

class VideoInfo(BaseModel):
    id: str = Field(..., description="비디오 ID")
    youtubeId: str = Field(..., description="YouTube 비디오 ID", example="dQw4w9WgXcQ")
    title: str = Field(..., description="비디오 제목", example="편의점 디저트 리뷰")
    channelTitle: str = Field(..., description="채널 이름", example="디저트리뷰")
    publishedAt: datetime = Field(..., description="게시 일자")
    viewCount: int = Field(..., description="조회수", example=12500)
    likeCount: int = Field(..., description="좋아요 수", example=850)
    commentCount: int = Field(..., description="댓글 수", example=120)
    thumbnailUrl: Optional[str] = Field(None, description="썸네일 URL")
    description: Optional[str] = Field(None, description="비디오 설명")
    sentimentAnalysis: Optional[SentimentAnalysisResult] = Field(None, description="감성 분석 결과")

class VideosList(BaseModel):
    items: List[VideoInfo]
    total: int = Field(..., description="총 비디오 수", example=120)
    page: int = Field(..., description="현재 페이지", example=1)
    pages: int = Field(..., description="총 페이지 수", example=12)
    limit: int = Field(..., description="페이지당 아이템 수", example=10)

class CommentInfo(BaseModel):
    id: str = Field(..., description="댓글 ID")
    text: str = Field(..., description="댓글 내용", example="이 디저트 정말 맛있어요!")
    authorName: str = Field(..., description="작성자 이름", example="디저트팬")
    authorProfileUrl: Optional[str] = Field(None, description="작성자 프로필 URL")
    publishedAt: datetime = Field(..., description="작성 일자")
    likeCount: int = Field(..., description="좋아요 수", example=15)
    sentimentLabel: Optional[str] = Field(None, description="감성 라벨", example="positive")
    sentimentScore: Optional[float] = Field(None, description="감성 점수 (-1 ~ 1)", example=0.75)

class VideoCommentsList(BaseModel):
    items: List[CommentInfo]
    total: int = Field(..., description="총 댓글 수", example=120)
    page: int = Field(..., description="현재 페이지", example=1)
    pages: int = Field(..., description="총 페이지 수", example=12)
    limit: int = Field(..., description="페이지당 아이템 수", example=50)
    videoInfo: Dict[str, Any] = Field(..., description="비디오 정보")

class DayTrendData(BaseModel):
    date: str = Field(..., description="날짜 (YYYY-MM-DD)", example="2023-07-28")
    positivePercentage: float = Field(..., description="긍정 비율 (%)", example=65.0)
    negativePercentage: float = Field(..., description="부정 비율 (%)", example=15.0)
    neutralPercentage: float = Field(..., description="중립 비율 (%)", example=20.0)
    averageScore: float = Field(..., description="평균 감성 점수", example=0.35)
    totalComments: int = Field(..., description="총 댓글 수", example=250)

class SentimentTrends(BaseModel):
    trends: List[DayTrendData]
    period: str = Field(..., description="기간", example="30days")

class ChannelInfo(BaseModel):
    channelId: str = Field(..., description="채널 ID")
    channelTitle: str = Field(..., description="채널 이름", example="디저트리뷰")
    videoCount: int = Field(..., description="비디오 수", example=25)
    commentCount: int = Field(..., description="댓글 수", example=560)
    averageSentiment: float = Field(..., description="평균 감성 점수", example=0.45)

class TopChannels(BaseModel):
    channels: List[ChannelInfo]

class KeywordInfo(BaseModel):
    keyword: str = Field(..., description="키워드", example="맛있다")
    count: int = Field(..., description="출현 횟수", example=125)
    sentiment: Optional[str] = Field(None, description="주요 감성", example="positive")
    score: Optional[float] = Field(None, description="평균 감성 점수", example=0.68)

class TopKeywords(BaseModel):
    keywords: List[KeywordInfo]
    sentiment: Optional[str] = Field(None, description="필터링된 감성", example="positive")


@router.get(
    "/summary", 
    response_model=DashboardSummary, 
    status_code=status.HTTP_200_OK, 
    summary="대시보드 요약 정보",
    description="""
    대시보드 화면에 표시할 요약 정보를 제공합니다.
    
    수집된 동영상 및 댓글 수, 최근 수집된 비디오 수, 감성 분석 분포, 최근 작업 상태 등을 포함합니다.
    프론트엔드 대시보드의 요약 패널을 위한 데이터로 사용됩니다.
    """,
    response_description="대시보드 요약 정보 및 통계"
)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    대시보드 요약 정보를 반환합니다.
    
    이 엔드포인트는 대시보드의 주요 지표를 요약하여 제공합니다:
    - 전체 수집된 동영상 및 댓글 수
    - 최근 7일간 수집된 동영상 수
    - 전체 댓글의 평균 감성 점수
    - 긍정/부정/중립 댓글 비율
    - 최근 데이터 수집 작업 상태
    
    Returns:
        Dict[str, Any]: 대시보드 요약 정보
    
    Examples:
        ```json
        {
          "totalVideos": 120,
          "totalComments": 3500,
          "recentVideos": 25,
          "averageSentiment": 0.35,
          "sentimentDistribution": {
            "positive": 0.65,
            "negative": 0.15,
            "neutral": 0.2
          },
          "recentJobs": [
            {
              "id": "123e4567-e89b-12d3-a456-426614174000",
              "type": "youtube_collection",
              "status": "completed",
              "progress": 100,
              "started_at": "2023-07-27T12:00:00Z",
              "completed_at": "2023-07-27T12:05:30Z"
            }
          ],
          "lastUpdated": "2023-07-28T08:30:45Z"
        }
        ```
    """
    # 동영상 및 댓글 수 집계
    video_count_query = await db.execute(func.count(YouTubeVideo.id))
    video_count = video_count_query.scalar() or 0
    
    comment_count_query = await db.execute(func.count(YouTubeComment.id))
    comment_count = comment_count_query.scalar() or 0
    
    # 최근 7일간 수집된 동영상 수
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_video_query = await db.execute(
        func.count(YouTubeVideo.id).filter(YouTubeVideo.created_at >= week_ago)
    )
    recent_video_count = recent_video_query.scalar() or 0
    
    # 감성 분석 통계
    sentiment_query = await db.execute(
        func.avg(YouTubeComment.sentiment_score).filter(YouTubeComment.sentiment_score.isnot(None))
    )
    avg_sentiment = sentiment_query.scalar() or 0.0
    
    # 긍정/부정/중립 댓글 비율
    positive_query = await db.execute(
        func.count(YouTubeComment.id).filter(YouTubeComment.sentiment_label == "positive")
    )
    positive_count = positive_query.scalar() or 0
    
    negative_query = await db.execute(
        func.count(YouTubeComment.id).filter(YouTubeComment.sentiment_label == "negative")
    )
    negative_count = negative_query.scalar() or 0
    
    neutral_query = await db.execute(
        func.count(YouTubeComment.id).filter(YouTubeComment.sentiment_label == "neutral")
    )
    neutral_count = neutral_query.scalar() or 0
    
    total_sentiment = positive_count + negative_count + neutral_count
    
    if total_sentiment > 0:
        sentiment_distribution = {
            "positive": positive_count / total_sentiment,
            "negative": negative_count / total_sentiment,
            "neutral": neutral_count / total_sentiment
        }
    else:
        sentiment_distribution = {
            "positive": 0,
            "negative": 0,
            "neutral": 0
        }
    
    # 최근 수집 작업 상태
    recent_jobs_query = await db.execute(
        crud_youtube.get_collection_jobs(db, limit=5, skip=0)
    )
    
    recent_jobs = []
    for job, _ in recent_jobs_query:
        recent_jobs.append({
            "id": job.id,
            "type": job.type,
            "status": job.status,
            "progress": job.progress,
            "started_at": job.started_at,
            "completed_at": job.completed_at
        })
    
    return {
        "totalVideos": video_count,
        "totalComments": comment_count,
        "recentVideos": recent_video_count,
        "averageSentiment": avg_sentiment,
        "sentimentDistribution": sentiment_distribution,
        "recentJobs": recent_jobs,
        "lastUpdated": datetime.utcnow()
    }


@router.get(
    "/videos", 
    response_model=VideosList, 
    status_code=status.HTTP_200_OK,
    summary="비디오 목록 조회",
    description="""
    대시보드에 표시할 YouTube 비디오 목록을 반환합니다.
    
    수집된 비디오 목록을 반환하며, 키워드 검색과 날짜 범위로 필터링이 가능합니다.
    각 비디오의 감성 분석 결과도 함께 제공합니다.
    페이지네이션을 지원하여 대량의 데이터를 효율적으로 검색할 수 있습니다.
    """,
    response_description="비디오 목록 및 감성 분석 결과"
)
async def get_dashboard_videos(
    limit: int = Query(10, ge=1, le=100, description="반환할 최대 항목 수"),
    skip: int = Query(0, ge=0, description="건너뛸 항목 수 (페이지네이션)"),
    keyword: Optional[str] = Query(None, description="검색 키워드 (제목, 설명에서 검색)"),
    start_date: Optional[datetime] = Query(None, description="시작 날짜 필터 (ISO 형식, 예: 2023-07-01T00:00:00Z)"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜 필터 (ISO 형식, 예: 2023-07-31T23:59:59Z)"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    대시보드용 동영상 목록을 반환합니다.
    
    다양한 필터링 옵션을 사용하여 수집된 YouTube 비디오 목록을 조회할 수 있습니다.
    각 비디오의 감성 분석 결과가 포함되어 있어 긍정/부정/중립 비율을 확인할 수 있습니다.
    
    Args:
        limit: 한 페이지에 반환할 최대 항목 수 (1-100)
        skip: 건너뛸 항목 수 (페이지네이션용)
        keyword: 제목이나 설명에서 검색할 키워드
        start_date: 게시일 기준 시작 날짜 필터
        end_date: 게시일 기준 종료 날짜 필터
        
    Returns:
        Dict[str, Any]: 동영상 목록 및 메타데이터
        
    Examples:
        ```json
        {
          "items": [
            {
              "id": "123e4567-e89b-12d3-a456-426614174000",
              "youtubeId": "dQw4w9WgXcQ",
              "title": "편의점 디저트 리뷰",
              "channelTitle": "디저트리뷰",
              "publishedAt": "2023-07-20T15:30:00Z",
              "viewCount": 12500,
              "likeCount": 850,
              "commentCount": 120,
              "thumbnailUrl": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
              "description": "편의점에서 구매한 디저트를 리뷰합니다...",
              "sentimentAnalysis": {
                "positivePercentage": 65.0,
                "negativePercentage": 15.0,
                "neutralPercentage": 20.0,
                "averageScore": 0.35
              }
            }
          ],
          "total": 120,
          "page": 1,
          "pages": 12,
          "limit": 10
        }
        ```
    """
    videos, total = await crud_youtube.get_youtube_videos(
        db=db,
        limit=limit,
        skip=skip,
        keyword=keyword,
        start_date=start_date,
        end_date=end_date,
        order_by="published_at",
        desc_order=True
    )
    
    video_list = []
    for video in videos:
        # 감성 분석 결과 가져오기
        sentiment_analysis = await crud_youtube.get_sentiment_analysis(db, video.id)
        
        video_data = {
            "id": video.id,
            "youtubeId": video.youtube_id,
            "title": video.title,
            "channelTitle": video.channel_title,
            "publishedAt": video.published_at,
            "viewCount": video.view_count,
            "likeCount": video.like_count,
            "commentCount": video.comment_count,
            "thumbnailUrl": video.thumbnail_url,
            "description": video.description[:200] + "..." if video.description and len(video.description) > 200 else video.description,
            "sentimentAnalysis": None
        }
        
        if sentiment_analysis:
            video_data["sentimentAnalysis"] = {
                "positivePercentage": sentiment_analysis.positive_percentage,
                "negativePercentage": sentiment_analysis.negative_percentage,
                "neutralPercentage": sentiment_analysis.neutral_percentage,
                "averageScore": sentiment_analysis.average_sentiment_score
            }
        
        video_list.append(video_data)
    
    return {
        "items": video_list,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "pages": (total + limit - 1) // limit if limit > 0 else 1,
        "limit": limit
    }


@router.get(
    "/videos/{video_id}/comments", 
    response_model=VideoCommentsList, 
    status_code=status.HTTP_200_OK,
    summary="비디오 댓글 목록 조회",
    description="""
    특정 비디오의 댓글 목록을 반환합니다.
    
    비디오 ID를 지정하여 해당 비디오에 달린 댓글 목록을 조회하며, 감성에 따른 필터링이 가능합니다.
    각 댓글의 감성 분석 결과(긍정/부정/중립)와 점수가 함께 제공됩니다.
    페이지네이션을 지원하여 많은 댓글을 효율적으로 탐색할 수 있습니다.
    """,
    response_description="댓글 목록, 비디오 정보 및 메타데이터",
    responses={
        404: {
            "description": "비디오를 찾을 수 없음",
            "content": {
                "application/json": {
                    "example": {"detail": "동영상을 찾을 수 없습니다"}
                }
            }
        }
    }
)
async def get_video_comments(
    video_id: str = Path(..., description="비디오 ID", examples={"value": "123e4567-e89b-12d3-a456-426614174000"}),
    limit: int = Query(50, ge=1, le=500, description="반환할 최대 항목 수"),
    skip: int = Query(0, ge=0, description="건너뛸 항목 수 (페이지네이션)"),
    sentiment: Optional[str] = Query(None, description="감성 필터 (positive, negative, neutral)"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    특정 동영상의 댓글 목록을 반환합니다.
    
    비디오 ID를 기준으로 특정 비디오에 달린 댓글을 조회합니다.
    감성별 필터링이 가능하여 긍정, 부정, 중립 댓글만 선택적으로 볼 수 있습니다.
    
    Args:
        video_id: 조회할 동영상 ID (UUID 형식)
        limit: 한 페이지에 반환할 최대 항목 수 (1-500)
        skip: 건너뛸 항목 수 (페이지네이션용)
        sentiment: 감성 필터 (positive, negative, neutral)
        
    Returns:
        Dict[str, Any]: 댓글 목록, 비디오 정보 및 메타데이터
        
    Raises:
        HTTPException: 비디오를 찾을 수 없는 경우
        
    Examples:
        ```json
        {
          "items": [
            {
              "id": "123e4567-e89b-12d3-a456-426614174001",
              "text": "이 디저트 정말 맛있어요!",
              "authorName": "디저트팬",
              "authorProfileUrl": "https://youtube.com/user/dessertfan",
              "publishedAt": "2023-07-21T18:45:30Z",
              "likeCount": 15,
              "sentimentLabel": "positive",
              "sentimentScore": 0.75
            },
            {
              "id": "123e4567-e89b-12d3-a456-426614174002",
              "text": "가격에 비해 양이 너무 적은 것 같아요",
              "authorName": "가성비킹",
              "authorProfileUrl": "https://youtube.com/user/valueconsumer",
              "publishedAt": "2023-07-21T19:15:20Z",
              "likeCount": 8,
              "sentimentLabel": "negative",
              "sentimentScore": -0.32
            }
          ],
          "total": 120,
          "page": 1,
          "pages": 3,
          "limit": 50,
          "videoInfo": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "편의점 디저트 리뷰",
            "youtubeId": "dQw4w9WgXcQ",
            "channelTitle": "디저트리뷰"
          }
        }
        ```
    """
    # 동영상 존재 확인
    video = await crud_youtube.get_youtube_video(db, video_id)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="동영상을 찾을 수 없습니다"
        )
    
    # 댓글 조회
    comments, total = await crud_youtube.get_youtube_comments(
        db=db,
        video_id=video.id,
        limit=limit,
        skip=skip,
        sentiment=sentiment,
        order_by="published_at",
        desc_order=True
    )
    
    comment_list = []
    for comment in comments:
        comment_data = {
            "id": comment.id,
            "text": comment.text,
            "authorName": comment.author_name,
            "authorProfileUrl": comment.author_profile_url,
            "publishedAt": comment.published_at,
            "likeCount": comment.like_count,
            "sentimentLabel": comment.sentiment_label,
            "sentimentScore": comment.sentiment_score
        }
        comment_list.append(comment_data)
    
    return {
        "items": comment_list,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "pages": (total + limit - 1) // limit if limit > 0 else 1,
        "limit": limit,
        "videoInfo": {
            "id": video.id,
            "title": video.title,
            "youtubeId": video.youtube_id,
            "channelTitle": video.channel_title
        }
    }


@router.get(
    "/sentiment/trends",
    response_model=SentimentTrends,
    status_code=status.HTTP_200_OK,
    summary="감성 분석 추세 조회",
    description="""
    지정된 기간 동안의 감성 분석 추세 데이터를 반환합니다.
    
    일별 감성 분석 결과의 추세를 확인할 수 있으며, 시간에 따른 감성 변화를 파악하는데 유용합니다.
    긍정/부정/중립 비율과 평균 감성 점수의 시계열 데이터를 제공합니다.
    """,
    response_description="일별 감성 분석 추세 데이터"
)
async def get_sentiment_trends(
    days: int = Query(30, ge=1, le=365, description="조회할 일수 (1-365)"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    지정된 기간 동안의 감성 분석 추세를 반환합니다.
    
    일별 감성 분석 결과를 시계열로 제공하여 시간에 따른 감성 변화 추세를 확인할 수 있습니다.
    각 날짜별로 긍정/부정/중립 댓글의 비율과 평균 감성 점수를 포함합니다.
    
    Args:
        days: 조회할 과거 일수 (기본값: 30일, 최대: 365일)
        
    Returns:
        Dict[str, Any]: 일별 감성 분석 추세 데이터
        
    Examples:
        ```json
        {
          "trends": [
            {
              "date": "2023-07-28",
              "positivePercentage": 68.5,
              "negativePercentage": 12.3,
              "neutralPercentage": 19.2,
              "averageScore": 0.42,
              "totalComments": 250
            },
            {
              "date": "2023-07-27",
              "positivePercentage": 65.2,
              "negativePercentage": 15.6,
              "neutralPercentage": 19.2,
              "averageScore": 0.38,
              "totalComments": 180
            }
          ],
          "period": "30days"
        }
        ```
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 일별 감성 분석 결과 집계 쿼리
    # 실제 구현에서는 SQLAlchemy로 날짜별 감성 점수 평균을 계산하는 쿼리 작성 필요
    # 여기서는 예시 데이터를 반환합니다
    
    # 예시 데이터 생성
    trends_data = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")
        
        # 날짜별로 약간의 변동이 있는 데이터 생성
        positive_percentage = 65.0 + (i % 7 - 3) * 2.0  # 55%~75% 사이 변동
        negative_percentage = 15.0 + (i % 5 - 2) * 1.5  # 7.5%~22.5% 사이 변동
        neutral_percentage = 100.0 - positive_percentage - negative_percentage
        average_score = 0.3 + (i % 10 - 5) * 0.05  # 0.05~0.55 사이 변동
        total_comments = 150 + (i % 7) * 30  # 150~330 사이 변동
        
        trends_data.append({
            "date": date_str,
            "positivePercentage": round(positive_percentage, 1),
            "negativePercentage": round(negative_percentage, 1),
            "neutralPercentage": round(neutral_percentage, 1),
            "averageScore": round(average_score, 2),
            "totalComments": total_comments
        })
    
    # 날짜 순서대로 정렬
    trends_data.sort(key=lambda x: x["date"])
    
    return {
        "trends": trends_data,
        "period": f"{days}days"
    }


@router.get(
    "/top-channels",
    response_model=TopChannels,
    status_code=status.HTTP_200_OK,
    summary="상위 채널 목록 조회",
    description="""
    댓글이 많은 상위 YouTube 채널 목록을 반환합니다.
    
    지정된 기간 동안 댓글 수가 많은 채널들을 조회하며, 각 채널의 비디오 수, 댓글 수, 평균 감성 점수 정보를 제공합니다.
    이를 통해 인기 있는 채널들의 영향력과 해당 채널에서의 감성 경향을 파악할 수 있습니다.
    """,
    response_description="상위 채널 목록 및 관련 통계"
)
async def get_top_channels(
    limit: int = Query(10, ge=1, le=50, description="반환할 채널 수 (1-50)"),
    days: int = Query(30, ge=1, le=365, description="조회할 일수 (1-365)"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    댓글이 많은 상위 채널 목록을 반환합니다.
    
    지정된 기간 동안 수집된 비디오 중에서 댓글이 가장 많은 채널들을 순위별로 정렬하여 제공합니다.
    각 채널별 비디오 수, 댓글 수, 평균 감성 점수 등의 통계 정보를 포함합니다.
    
    Args:
        limit: 반환할 채널 수 (기본값: 10, 최대: 50)
        days: 조회할 과거 일수 (기본값: 30일, 최대: 365일)
        
    Returns:
        Dict[str, Any]: 상위 채널 목록 및 기간 정보
        
    Examples:
        ```json
        {
          "channels": [
            {
              "channelId": "UC1zEtT2-_RS_PdZlp8tX1Yg",
              "channelTitle": "디저트리뷰",
              "videoCount": 25,
              "commentCount": 3200,
              "averageSentiment": 0.68
            },
            {
              "channelId": "UC9vU-R2MEnw22tXIAMLKQHw",
              "channelTitle": "편의점 미식가",
              "videoCount": 18,
              "commentCount": 2800,
              "averageSentiment": 0.42
            }
          ],
          "period": {
            "start": "2023-06-29T00:00:00Z",
            "end": "2023-07-29T00:00:00Z"
          }
        }
        ```
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # 채널별 동영상 및 댓글 수 집계 쿼리
    query = """
    SELECT
        v.channel_id,
        v.channel_title,
        COUNT(DISTINCT v.id) as video_count,
        SUM(v.comment_count) as comment_count,
        AVG(s.average_sentiment_score) as avg_sentiment
    FROM
        youtube_videos v
    LEFT JOIN
        youtube_sentiment_analysis s ON v.id = s.video_id
    WHERE
        v.published_at >= :start_date
    GROUP BY
        v.channel_id, v.channel_title
    ORDER BY
        comment_count DESC
    LIMIT :limit
    """
    
    result = await db.execute(query, {"start_date": start_date, "limit": limit})
    
    channels = []
    for row in result:
        channels.append({
            "channelId": row.channel_id,
            "channelTitle": row.channel_title,
            "videoCount": row.video_count,
            "commentCount": row.comment_count,
            "averageSentiment": row.avg_sentiment if row.avg_sentiment is not None else 0.0
        })
    
    return {
        "channels": channels,
        "period": {
            "start": start_date,
            "end": datetime.utcnow()
        }
    }


@router.get(
    "/keywords",
    response_model=TopKeywords,
    status_code=status.HTTP_200_OK,
    summary="상위 키워드 분석 결과 조회",
    description="""
    댓글에서 추출된 상위 키워드 분석 결과를 반환합니다.
    
    지정된 기간 동안 댓글에서 자주 등장하는 키워드들을 빈도와 감성 정보와 함께 제공합니다.
    특정 감성(긍정/부정/중립)으로 필터링할 수 있어 긍정적인 키워드나 부정적인 키워드만 조회 가능합니다.
    이를 통해 소비자들이 자주 언급하는 주제와 그에 대한 감성을 파악할 수 있습니다.
    """,
    response_description="상위 키워드 목록 및 감성 정보"
)
async def get_top_keywords(
    days: int = Query(30, ge=1, le=365, description="조회할 일수 (1-365)"),
    sentiment: Optional[str] = Query(None, description="감성 필터 (positive, negative, neutral, all)"),
    limit: int = Query(20, ge=1, le=100, description="반환할 키워드 수 (1-100)"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    최근 키워드 분석 결과를 반환합니다.
    
    지정된 기간 동안 수집된 댓글에서 추출된 주요 키워드들을 빈도순으로 정렬하여 제공합니다.
    각 키워드별로 출현 횟수와 주요 감성 정보가 포함되며, 특정 감성으로 필터링할 수 있습니다.
    
    Args:
        days: 조회할 과거 일수 (기본값: 30일, 최대: 365일)
        sentiment: 감성 필터 (positive, negative, neutral, all)
        limit: 반환할 키워드 수 (기본값: 20, 최대: 100)
        
    Returns:
        Dict[str, Any]: 키워드 분석 결과 및 기간 정보
        
    Examples:
        ```json
        {
          "keywords": [
            {
              "keyword": "맛있다",
              "count": 245,
              "sentiment": "positive",
              "score": 0.78
            },
            {
              "keyword": "가격",
              "count": 187,
              "sentiment": "neutral",
              "score": 0.12
            },
            {
              "keyword": "달콤한",
              "count": 156,
              "sentiment": "positive",
              "score": 0.65
            }
          ],
          "sentiment": "all",
          "period": {
            "start": "2023-06-29T00:00:00Z",
            "end": "2023-07-29T00:00:00Z"
          }
        }
        ```
    """
    # 실제 구현에서는 분석된 키워드를 가져오는 로직 구현 필요
    # 여기서는 예시 데이터를 반환합니다
    
    # 기본 키워드 목록
    keywords_list = [
        {"keyword": "맛있다", "count": 245, "sentiment": "positive", "score": 0.78},
        {"keyword": "가격", "count": 187, "sentiment": "neutral", "score": 0.12},
        {"keyword": "달콤한", "count": 156, "sentiment": "positive", "score": 0.65},
        {"keyword": "비싸다", "count": 142, "sentiment": "negative", "score": -0.52},
        {"keyword": "추천", "count": 138, "sentiment": "positive", "score": 0.85},
        {"keyword": "리뷰", "count": 129, "sentiment": "neutral", "score": 0.05},
        {"keyword": "신상", "count": 115, "sentiment": "neutral", "score": 0.18},
        {"keyword": "재구매", "count": 98, "sentiment": "positive", "score": 0.91},
        {"keyword": "실망", "count": 87, "sentiment": "negative", "score": -0.68},
        {"keyword": "맛없다", "count": 75, "sentiment": "negative", "score": -0.82},
        {"keyword": "촉촉한", "count": 73, "sentiment": "positive", "score": 0.72},
        {"keyword": "단맛", "count": 72, "sentiment": "neutral", "score": 0.25},
        {"keyword": "배송", "count": 68, "sentiment": "neutral", "score": -0.15},
        {"keyword": "패키지", "count": 65, "sentiment": "neutral", "score": 0.30},
        {"keyword": "가성비", "count": 63, "sentiment": "positive", "score": 0.58},
        {"keyword": "신제품", "count": 58, "sentiment": "neutral", "score": 0.22},
        {"keyword": "식감", "count": 55, "sentiment": "positive", "score": 0.62},
        {"keyword": "포장", "count": 52, "sentiment": "neutral", "score": 0.10},
        {"keyword": "편의점", "count": 48, "sentiment": "neutral", "score": 0.08},
        {"keyword": "품절", "count": 45, "sentiment": "negative", "score": -0.45},
        {"keyword": "달달", "count": 43, "sentiment": "positive", "score": 0.75},
        {"keyword": "수입", "count": 40, "sentiment": "neutral", "score": 0.20},
        {"keyword": "이벤트", "count": 38, "sentiment": "positive", "score": 0.50},
        {"keyword": "할인", "count": 36, "sentiment": "positive", "score": 0.60},
        {"keyword": "양", "count": 35, "sentiment": "negative", "score": -0.35}
    ]
    
    # 감성 필터링
    if sentiment and sentiment != "all":
        keywords_list = [k for k in keywords_list if k["sentiment"] == sentiment]
    
    # 상위 키워드 추출
    keywords_list = keywords_list[:limit]
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    return {
        "keywords": keywords_list,
        "sentiment": sentiment if sentiment else "all",
        "period": {
            "start": start_date,
            "start": datetime.utcnow() - timedelta(days=days),
            "end": datetime.utcnow()
        }
    } 