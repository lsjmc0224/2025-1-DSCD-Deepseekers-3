"""
YouTube CRUD 함수 테스트

YouTube 관련 CRUD 함수의 기능을 검증하는 테스트 모음입니다.
"""

import sys
import os
import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, List

# 테스트가 필요한 모듈 경로 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# 테스트 대상 모듈
from app.crud import youtube
from app.models.youtube_data import YouTubeVideo, YouTubeComment, YouTubeSentimentAnalysis, CollectionJob
from app.db.session import get_db


# YouTube 비디오 CRUD 테스트
@pytest.mark.asyncio
async def test_create_youtube_video(db_session):
    """YouTube 비디오 생성 함수 테스트"""
    # 테스트 데이터
    video_data = {
        "youtube_id": "test_video_id",
        "title": "테스트 비디오 제목",
        "description": "테스트 비디오 설명",
        "channel_id": "test_channel_id",
        "channel_title": "테스트 채널",
        "published_at": datetime.now() - timedelta(days=1),
        "view_count": 1000,
        "like_count": 100,
        "comment_count": 50,
        "thumbnail_url": "https://example.com/thumbnail.jpg"
    }
    
    # CRUD 함수 호출
    created_video = await youtube.create_youtube_video(db_session, video_data)
    
    # 결과 검증
    assert created_video is not None
    assert created_video.youtube_id == video_data["youtube_id"]
    assert created_video.title == video_data["title"]
    assert created_video.channel_id == video_data["channel_id"]
    assert created_video.view_count == video_data["view_count"]
    assert created_video.comment_count == video_data["comment_count"]


@pytest.mark.asyncio
async def test_get_youtube_video(db_session):
    """YouTube 비디오 조회 함수 테스트"""
    # 비디오 먼저 생성
    video_data = {
        "youtube_id": "test_video_id",
        "title": "테스트 비디오 제목",
        "channel_id": "test_channel_id",
        "channel_title": "테스트 채널",
        "published_at": datetime.now() - timedelta(days=1)
    }
    created_video = await youtube.create_youtube_video(db_session, video_data)
    
    # CRUD 함수 호출
    video = await youtube.get_youtube_video(db_session, "test_video_id")
    
    # 결과 검증
    assert video is not None
    assert video.youtube_id == "test_video_id"
    assert video.title == "테스트 비디오 제목"
    assert video.channel_id == "test_channel_id"


@pytest.mark.asyncio
async def test_get_youtube_videos(db_session):
    """YouTube 비디오 목록 조회 함수 테스트"""
    # 비디오 여러 개 생성
    video_data1 = {
        "youtube_id": "test_video_id1",
        "title": "테스트 비디오 1",
        "channel_id": "test_channel_id",
        "channel_title": "테스트 채널",
        "published_at": datetime.now() - timedelta(days=2)
    }
    
    video_data2 = {
        "youtube_id": "test_video_id2",
        "title": "테스트 비디오 2",
        "channel_id": "test_channel_id",
        "channel_title": "테스트 채널",
        "published_at": datetime.now() - timedelta(days=1)
    }
    
    await youtube.create_youtube_video(db_session, video_data1)
    await youtube.create_youtube_video(db_session, video_data2)
    
    # CRUD 함수 호출 (필터 없이)
    videos, total = await youtube.get_youtube_videos(db_session)
    
    # 결과 검증
    assert videos is not None
    assert len(videos) >= 2
    assert total >= 2
    
    # 채널 ID로 필터링
    videos, total = await youtube.get_youtube_videos(db_session, channel_id="test_channel_id")
    
    # 결과 검증
    assert videos is not None
    assert len(videos) >= 2
    assert total >= 2
    assert all(v.channel_id == "test_channel_id" for v in videos)
    
    # 키워드로 필터링
    videos, total = await youtube.get_youtube_videos(db_session, keyword="테스트")
    
    # 결과 검증
    assert videos is not None
    assert len(videos) >= 2
    assert total >= 2
    
    # 페이지네이션 테스트
    videos, total = await youtube.get_youtube_videos(db_session, skip=0, limit=1)
    
    # 결과 검증
    assert videos is not None
    assert len(videos) == 1
    assert total >= 2


# YouTube 댓글 CRUD 테스트
@pytest.mark.asyncio
async def test_create_youtube_comment(db_session):
    """YouTube 댓글 생성 함수 테스트"""
    # 먼저 비디오 생성
    video_data = {
        "youtube_id": "test_video_id",
        "title": "테스트 비디오 제목",
        "channel_id": "test_channel_id",
        "channel_title": "테스트 채널",
        "published_at": datetime.now() - timedelta(days=1)
    }
    await youtube.create_youtube_video(db_session, video_data)
    
    # 테스트 데이터
    comment_data = {
        "comment_id": "test_comment_id",
        "video_id": "test_video_id",
        "text": "테스트 댓글 내용입니다.",
        "author_name": "테스트 사용자",
        "author_profile_url": "https://example.com/user",
        "published_at": datetime.now() - timedelta(hours=12),
        "like_count": 5
    }
    
    # CRUD 함수 호출
    created_comment = await youtube.create_youtube_comment(db_session, comment_data)
    
    # 결과 검증
    assert created_comment is not None
    assert created_comment.comment_id == comment_data["comment_id"]
    assert created_comment.video_id == comment_data["video_id"]
    assert created_comment.text == comment_data["text"]
    assert created_comment.author_name == comment_data["author_name"]
    assert created_comment.like_count == comment_data["like_count"]


@pytest.mark.asyncio
async def test_get_youtube_comments(db_session):
    """YouTube 댓글 목록 조회 함수 테스트"""
    # 먼저 비디오 생성
    video_data = {
        "youtube_id": "test_video_id",
        "title": "테스트 비디오 제목",
        "channel_id": "test_channel_id",
        "channel_title": "테스트 채널",
        "published_at": datetime.now() - timedelta(days=1)
    }
    await youtube.create_youtube_video(db_session, video_data)
    
    # 댓글 여러 개 생성
    comment_data1 = {
        "comment_id": "test_comment_id1",
        "video_id": "test_video_id",
        "text": "첫 번째 테스트 댓글",
        "author_name": "사용자1",
        "published_at": datetime.now() - timedelta(hours=12)
    }
    
    comment_data2 = {
        "comment_id": "test_comment_id2",
        "video_id": "test_video_id",
        "text": "두 번째 테스트 댓글",
        "author_name": "사용자2",
        "published_at": datetime.now() - timedelta(hours=6)
    }
    
    await youtube.create_youtube_comment(db_session, comment_data1)
    await youtube.create_youtube_comment(db_session, comment_data2)
    
    # CRUD 함수 호출
    comments, total = await youtube.get_youtube_comments(db_session, video_id="test_video_id")
    
    # 결과 검증
    assert comments is not None
    assert len(comments) >= 2
    assert total >= 2
    assert all(c.video_id == "test_video_id" for c in comments)
    
    # 페이지네이션 테스트
    comments, total = await youtube.get_youtube_comments(db_session, video_id="test_video_id", skip=0, limit=1)
    
    # 결과 검증
    assert comments is not None
    assert len(comments) == 1
    assert total >= 2


# YouTube 감성 분석 CRUD 테스트
@pytest.mark.asyncio
async def test_create_sentiment_analysis(db_session):
    """감성 분석 결과 생성 함수 테스트"""
    # 먼저 비디오 생성
    video_data = {
        "youtube_id": "test_video_id",
        "title": "테스트 비디오 제목",
        "channel_id": "test_channel_id",
        "channel_title": "테스트 채널",
        "published_at": datetime.now() - timedelta(days=1)
    }
    await youtube.create_youtube_video(db_session, video_data)
    
    # 테스트 데이터
    sentiment_data = {
        "video_id": "test_video_id",
        "positive_count": 35,
        "negative_count": 10,
        "neutral_count": 5,
        "positive_percentage": 70.0,
        "negative_percentage": 20.0,
        "neutral_percentage": 10.0,
        "average_sentiment_score": 0.65
    }
    
    # CRUD 함수 호출
    created_sentiment = await youtube.create_sentiment_analysis(db_session, sentiment_data)
    
    # 결과 검증
    assert created_sentiment is not None
    assert created_sentiment.video_id == sentiment_data["video_id"]
    assert created_sentiment.positive_count == sentiment_data["positive_count"]
    assert created_sentiment.negative_count == sentiment_data["negative_count"]
    assert created_sentiment.neutral_count == sentiment_data["neutral_count"]
    assert created_sentiment.positive_percentage == sentiment_data["positive_percentage"]
    assert created_sentiment.average_sentiment_score == sentiment_data["average_sentiment_score"]


@pytest.mark.asyncio
async def test_get_sentiment_analysis(db_session):
    """감성 분석 결과 조회 함수 테스트"""
    # 먼저 비디오 생성
    video_data = {
        "youtube_id": "test_video_id",
        "title": "테스트 비디오 제목",
        "channel_id": "test_channel_id",
        "channel_title": "테스트 채널",
        "published_at": datetime.now() - timedelta(days=1)
    }
    await youtube.create_youtube_video(db_session, video_data)
    
    # 감성 분석 생성
    sentiment_data = {
        "video_id": "test_video_id",
        "positive_count": 35,
        "negative_count": 10,
        "neutral_count": 5,
        "positive_percentage": 70.0,
        "negative_percentage": 20.0,
        "neutral_percentage": 10.0,
        "average_sentiment_score": 0.65
    }
    await youtube.create_sentiment_analysis(db_session, sentiment_data)
    
    # CRUD 함수 호출
    sentiment = await youtube.get_sentiment_analysis(db_session, "test_video_id")
    
    # 결과 검증
    assert sentiment is not None
    assert sentiment.video_id == "test_video_id"
    assert sentiment.positive_count == 35
    assert sentiment.negative_count == 10
    assert sentiment.neutral_count == 5
    assert sentiment.positive_percentage == 70.0
    assert sentiment.average_sentiment_score == 0.65


# 수집 작업 CRUD 테스트
@pytest.mark.asyncio
async def test_create_collection_job(db_session):
    """수집 작업 생성 함수 테스트"""
    # 테스트 데이터
    job_data = {
        "id": "test_job_id",
        "type": "youtube_collection",
        "status": "pending",
        "parameters": {
            "video_ids": ["test_video_id"],
            "max_comments": 100
        }
    }
    
    # CRUD 함수 호출
    created_job = await youtube.create_collection_job(db_session, job_data)
    
    # 결과 검증
    assert created_job is not None
    assert created_job.id == job_data["id"]
    assert created_job.type == job_data["type"]
    assert created_job.status == job_data["status"]
    assert created_job.parameters["video_ids"] == job_data["parameters"]["video_ids"]
    assert created_job.parameters["max_comments"] == job_data["parameters"]["max_comments"]
    assert created_job.started_at is not None
    assert created_job.completed_at is None


@pytest.mark.asyncio
async def test_update_collection_job(db_session):
    """수집 작업 업데이트 함수 테스트"""
    # 먼저 작업 생성
    job_data = {
        "id": "test_job_id",
        "type": "youtube_collection",
        "status": "pending",
        "parameters": {
            "video_ids": ["test_video_id"],
            "max_comments": 100
        }
    }
    await youtube.create_collection_job(db_session, job_data)
    
    # 업데이트 데이터
    update_data = {
        "status": "completed",
        "result": {
            "videos_collected": 1,
            "comments_collected": 50
        }
    }
    
    # CRUD 함수 호출
    updated_job = await youtube.update_collection_job(db_session, "test_job_id", update_data)
    
    # 결과 검증
    assert updated_job is not None
    assert updated_job.id == "test_job_id"
    assert updated_job.status == "completed"
    assert updated_job.result["videos_collected"] == 1
    assert updated_job.result["comments_collected"] == 50
    assert updated_job.started_at is not None
    assert updated_job.completed_at is not None


@pytest.mark.asyncio
async def test_get_collection_job(db_session):
    """수집 작업 조회 함수 테스트"""
    # 먼저 작업 생성
    job_data = {
        "id": "test_job_id",
        "type": "youtube_collection",
        "status": "completed",
        "parameters": {
            "video_ids": ["test_video_id"],
            "max_comments": 100
        },
        "result": {
            "videos_collected": 1,
            "comments_collected": 50
        }
    }
    await youtube.create_collection_job(db_session, job_data)
    
    # CRUD 함수 호출
    job = await youtube.get_collection_job(db_session, "test_job_id")
    
    # 결과 검증
    assert job is not None
    assert job.id == "test_job_id"
    assert job.type == "youtube_collection"
    assert job.status == "completed"
    assert job.parameters["video_ids"] == ["test_video_id"]
    assert job.result["videos_collected"] == 1


@pytest.mark.asyncio
async def test_get_collection_jobs(db_session):
    """수집 작업 목록 조회 함수 테스트"""
    # 작업 여러 개 생성
    job_data1 = {
        "id": "test_job_id1",
        "type": "youtube_collection",
        "status": "completed",
        "parameters": {"video_ids": ["video1"]}
    }
    
    job_data2 = {
        "id": "test_job_id2",
        "type": "youtube_collection",
        "status": "pending",
        "parameters": {"video_ids": ["video2"]}
    }
    
    await youtube.create_collection_job(db_session, job_data1)
    await youtube.create_collection_job(db_session, job_data2)
    
    # CRUD 함수 호출 (필터 없이)
    jobs, total = await youtube.get_collection_jobs(db_session)
    
    # 결과 검증
    assert jobs is not None
    assert len(jobs) >= 2
    assert total >= 2
    
    # 상태로 필터링
    jobs, total = await youtube.get_collection_jobs(db_session, status="completed")
    
    # 결과 검증
    assert jobs is not None
    assert len(jobs) >= 1
    assert total >= 1
    assert all(j.status == "completed" for j in jobs)
    
    # 페이지네이션 테스트
    jobs, total = await youtube.get_collection_jobs(db_session, limit=1, skip=0)
    
    # 결과 검증
    assert jobs is not None
    assert len(jobs) == 1
    assert total >= 2 