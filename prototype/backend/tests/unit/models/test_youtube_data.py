"""
YouTube 데이터 모델 테스트

YouTube 관련 데이터 모델의 기능을 검증하는 테스트 모음입니다.
"""

import sys
import os
import pytest
from datetime import datetime, timedelta
from sqlalchemy import text

# 테스트가 필요한 모듈 경로 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# 테스트 대상 모듈
from app.models.youtube_data import YouTubeVideo, YouTubeComment, YouTubeSentimentAnalysis, CollectionJob


# 모델 인스턴스 생성 및 속성 테스트
@pytest.mark.asyncio
async def test_youtube_video_model(db_session):
    """YouTubeVideo 모델 생성 및 속성 테스트"""
    # 비디오 인스턴스 생성
    video = YouTubeVideo(
        youtube_id="test_video_id",
        title="테스트 비디오 제목",
        description="테스트 비디오 설명",
        channel_id="test_channel_id",
        channel_title="테스트 채널",
        published_at=datetime.now() - timedelta(days=1),
        view_count=1000,
        like_count=100,
        comment_count=50,
        thumbnail_url="https://example.com/thumbnail.jpg"
    )
    
    # DB에 저장
    db_session.add(video)
    await db_session.commit()
    await db_session.refresh(video)
    
    # DB에서 조회
    result = await db_session.get(YouTubeVideo, video.id)
    
    # 결과 검증
    assert result is not None
    assert result.youtube_id == "test_video_id"
    assert result.title == "테스트 비디오 제목"
    assert result.channel_id == "test_channel_id"
    assert result.view_count == 1000
    assert result.comment_count == 50


@pytest.mark.asyncio
async def test_youtube_comment_model(db_session):
    """YouTubeComment 모델 생성 및 속성 테스트"""
    # 먼저 비디오 생성
    video = YouTubeVideo(
        youtube_id="test_video_id",
        title="테스트 비디오 제목",
        channel_id="test_channel_id",
        channel_title="테스트 채널",
        published_at=datetime.now() - timedelta(days=1)
    )
    db_session.add(video)
    await db_session.commit()
    await db_session.refresh(video)
    
    # 댓글 인스턴스 생성
    comment = YouTubeComment(
        comment_id="test_comment_id",
        video_id=video.youtube_id,
        text="테스트 댓글 내용입니다.",
        author_name="테스트 사용자",
        author_profile_url="https://example.com/user",
        published_at=datetime.now() - timedelta(hours=12),
        like_count=5
    )
    
    # DB에 저장
    db_session.add(comment)
    await db_session.commit()
    await db_session.refresh(comment)
    
    # DB에서 조회
    result = await db_session.get(YouTubeComment, comment.id)
    
    # 결과 검증
    assert result is not None
    assert result.comment_id == "test_comment_id"
    assert result.video_id == "test_video_id"
    assert result.text == "테스트 댓글 내용입니다."
    assert result.author_name == "테스트 사용자"
    assert result.like_count == 5


@pytest.mark.asyncio
async def test_youtube_sentiment_analysis_model(db_session):
    """YouTubeSentimentAnalysis 모델 생성 및 속성 테스트"""
    # 먼저 비디오 생성
    video = YouTubeVideo(
        youtube_id="test_video_id",
        title="테스트 비디오 제목",
        channel_id="test_channel_id",
        channel_title="테스트 채널",
        published_at=datetime.now() - timedelta(days=1)
    )
    db_session.add(video)
    await db_session.commit()
    await db_session.refresh(video)
    
    # 감성 분석 인스턴스 생성
    sentiment = YouTubeSentimentAnalysis(
        video_id=video.youtube_id,
        positive_count=35,
        negative_count=10,
        neutral_count=5,
        positive_percentage=70.0,
        negative_percentage=20.0,
        neutral_percentage=10.0,
        average_sentiment_score=0.65
    )
    
    # DB에 저장
    db_session.add(sentiment)
    await db_session.commit()
    await db_session.refresh(sentiment)
    
    # DB에서 조회
    result = await db_session.get(YouTubeSentimentAnalysis, sentiment.id)
    
    # 결과 검증
    assert result is not None
    assert result.video_id == "test_video_id"
    assert result.positive_count == 35
    assert result.negative_count == 10
    assert result.neutral_count == 5
    assert result.positive_percentage == 70.0
    assert result.average_sentiment_score == 0.65


@pytest.mark.asyncio
async def test_collection_job_model(db_session):
    """CollectionJob 모델 생성 및 속성 테스트"""
    # 수집 작업 인스턴스 생성
    job = CollectionJob(
        id="test_job_id",
        type="youtube_collection",
        status="completed",
        parameters={
            "video_ids": ["test_video_id"],
            "max_comments": 100
        },
        result={
            "videos_collected": 1,
            "comments_collected": 50
        },
        started_at=datetime.now() - timedelta(hours=2),
        completed_at=datetime.now() - timedelta(hours=1)
    )
    
    # DB에 저장
    db_session.add(job)
    await db_session.commit()
    await db_session.refresh(job)
    
    # DB에서 조회
    result = await db_session.get(CollectionJob, job.id)
    
    # 결과 검증
    assert result is not None
    assert result.id == "test_job_id"
    assert result.type == "youtube_collection"
    assert result.status == "completed"
    assert result.parameters["video_ids"] == ["test_video_id"]
    assert result.result["videos_collected"] == 1
    assert result.result["comments_collected"] == 50
    assert result.started_at is not None
    assert result.completed_at is not None


@pytest.mark.asyncio
async def test_youtube_relationships(db_session):
    """모델 간 관계 테스트"""
    # 비디오 생성
    video = YouTubeVideo(
        youtube_id="test_video_id",
        title="테스트 비디오 제목",
        channel_id="test_channel_id",
        channel_title="테스트 채널",
        published_at=datetime.now() - timedelta(days=1)
    )
    db_session.add(video)
    await db_session.commit()
    await db_session.refresh(video)
    
    # 댓글 생성
    comment = YouTubeComment(
        comment_id="test_comment_id",
        video_id=video.youtube_id,
        text="테스트 댓글 내용입니다.",
        author_name="테스트 사용자",
        published_at=datetime.now() - timedelta(hours=12)
    )
    db_session.add(comment)
    
    # 감성 분석 생성
    sentiment = YouTubeSentimentAnalysis(
        video_id=video.youtube_id,
        positive_count=35,
        negative_count=10,
        neutral_count=5,
        positive_percentage=70.0,
        negative_percentage=20.0,
        neutral_percentage=10.0,
        average_sentiment_score=0.65
    )
    db_session.add(sentiment)
    await db_session.commit()
    
    # 관계 검증 (SQLAlchemy 모델에 관계가 정의되어 있는 경우)
    # 비디오 객체를 통해 댓글 목록 조회
    from sqlalchemy import select
    
    # 비디오에 해당하는 댓글 조회
    stmt = select(YouTubeComment).where(YouTubeComment.video_id == video.youtube_id)
    result = await db_session.execute(stmt)
    comments = result.scalars().all()
    assert len(comments) == 1
    assert comments[0].comment_id == "test_comment_id"
    
    # 비디오에 해당하는 감성 분석 조회
    stmt = select(YouTubeSentimentAnalysis).where(YouTubeSentimentAnalysis.video_id == video.youtube_id)
    result = await db_session.execute(stmt)
    sentiments = result.scalars().all()
    assert len(sentiments) == 1
    assert sentiments[0].positive_count == 35 