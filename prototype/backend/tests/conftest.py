"""
테스트 고정장치(Fixtures) 구성 파일

pytest 프레임워크를 위한 공통 픽스처 모음입니다.
테스트 데이터베이스, API 클라이언트, 모의 데이터 등을 설정합니다.
"""

import os
import sys
import pytest
import pytest_asyncio
import asyncio
from typing import Generator, Any, Dict, List, AsyncGenerator
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# pytest-asyncio 설정
pytest_plugins = ["pytest_asyncio"]
pytest.asyncio_default_fixture_loop_scope = "function"

# 상위 디렉토리 추가하여 app 모듈 import 가능하게 함
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# 테스트할 애플리케이션 모듈 가져오기
from app.db.session import get_db
from app.db.base import Base
from app.core.config import settings
from main import app as fastapi_app


# 테스트 데이터베이스 설정
TEST_SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_SQLALCHEMY_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(
    bind=test_engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


# 테스트용 API 클라이언트와 데이터베이스 세션 제공
@pytest.fixture
def app() -> FastAPI:
    """테스트용 FastAPI 앱 인스턴스를 반환합니다."""
    return fastapi_app


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    """테스트용 FastAPI 클라이언트를 반환합니다."""
    return TestClient(app)


# 비동기 테스트를 위한 이벤트 루프 제공
@pytest.fixture(scope="session")
def event_loop():
    """pytest-asyncio를 위한 이벤트 루프 픽스처입니다."""
    try:
        loop = asyncio.get_event_loop_policy().new_event_loop()
        yield loop
    finally:
        loop.close()


# 테스트용 데이터베이스 세션 제공
@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """테스트용 비동기 DB 세션을 제공합니다."""
    # 메모리 DB에 테이블 생성
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 세션 생성
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        await session.close()
    
    # 테스트 종료 후 테이블 삭제
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# 데이터베이스 세션 모킹 픽스처
@pytest.fixture
def mock_get_db():
    """get_db 함수를 모킹하는 픽스처를 제공합니다."""
    with patch('app.db.session.get_db') as _mock:
        yield _mock


# 의존성 오버라이드를 위한 API 클라이언트
@pytest.fixture
async def client_with_db(app: FastAPI, db_session: AsyncSession) -> TestClient:
    """DB 세션이 오버라이드된 테스트 클라이언트를 제공합니다."""
    
    async def _get_test_db():
        yield db_session
    
    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides = {}


# 모의 YouTube 비디오 데이터 제공
@pytest.fixture
def mock_youtube_video() -> Dict[str, Any]:
    """테스트용 YouTube 비디오 데이터를 제공합니다."""
    return {
        "youtube_id": "test_video_id",
        "title": "테스트 비디오",
        "description": "테스트 비디오 설명입니다.",
        "channel_id": "test_channel_id",
        "channel_title": "테스트 채널",
        "published_at": datetime.now() - timedelta(days=1),
        "view_count": 1000,
        "like_count": 100,
        "comment_count": 50,
        "thumbnail_url": "https://example.com/thumbnail.jpg"
    }


# 모의 YouTube 댓글 데이터 제공
@pytest.fixture
def mock_youtube_comments() -> List[Dict[str, Any]]:
    """테스트용 YouTube 댓글 데이터를 제공합니다."""
    return [
        {
            "comment_id": "comment1",
            "text": "좋은 영상입니다!",
            "author_name": "사용자1",
            "author_profile_url": "https://example.com/user1",
            "published_at": datetime.now() - timedelta(days=1),
            "like_count": 10,
            "video_id": "test_video_id"
        },
        {
            "comment_id": "comment2",
            "text": "정보가 유익해요.",
            "author_name": "사용자2",
            "author_profile_url": "https://example.com/user2",
            "published_at": datetime.now() - timedelta(hours=12),
            "like_count": 5,
            "video_id": "test_video_id"
        }
    ]


# 모의 감성 분석 결과 제공
@pytest.fixture
def mock_sentiment_analysis() -> Dict[str, Any]:
    """테스트용 감성 분석 결과를 제공합니다."""
    return {
        "video_id": "test_video_id",
        "positive_count": 35,
        "negative_count": 10,
        "neutral_count": 5,
        "positive_percentage": 70.0,
        "negative_percentage": 20.0,
        "neutral_percentage": 10.0,
        "average_score": 0.65
    }


# 모의 수집 작업 데이터 제공
@pytest.fixture
def mock_collection_job() -> Dict[str, Any]:
    """테스트용 수집 작업 데이터를 제공합니다."""
    return {
        "job_id": "test_job_id",
        "type": "youtube_collection",
        "status": "completed",
        "parameters": {
            "video_ids": ["test_video_id"],
            "max_comments": 100
        },
        "result": {
            "videos_collected": 1,
            "comments_collected": 50
        },
        "created_at": datetime.now() - timedelta(hours=2),
        "updated_at": datetime.now() - timedelta(hours=1),
        "completed_at": datetime.now() - timedelta(minutes=30)
    }


# 모의 Redis 클라이언트 제공
@pytest.fixture
def mock_redis_client() -> MagicMock:
    """테스트용 Redis 클라이언트 모의 객체를 제공합니다."""
    mock_redis = MagicMock()
    
    # 자주 사용되는 메서드에 대한 기본 반환값 설정
    async def mock_get(key):
        if key == "job:test_job_id":
            return '{"status": "completed", "progress": 100}'
        return None
    
    async def mock_set(key, value, ex=None):
        return True
    
    mock_redis.get = mock_get
    mock_redis.set = mock_set
    
    return mock_redis 