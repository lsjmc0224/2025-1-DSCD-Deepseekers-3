"""
헬스체크 API 엔드포인트

시스템 상태 확인을 위한 엔드포인트를 제공합니다.
"""

from typing import Dict, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

# 라우터 정의
router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def health_check(
    db: AsyncSession = Depends(get_db)
):
    """
    시스템 상태를 확인합니다.
    
    데이터베이스 연결, 외부 서비스 연결 등을 체크합니다.
    """
    # TODO: 실제 서비스 연결 체크 로직 구현
    return {
        "status": "ok",
        "services": {
            "database": "connected",
            "redis": "connected",
            "s3": "connected",
            "prefect": "connected"
        },
        "version": "1.0.0"
    }


@router.get("/db", response_model=Dict[str, Any])
async def db_health_check(
    db: AsyncSession = Depends(get_db)
):
    """
    데이터베이스 연결 상태를 확인합니다.
    """
    try:
        # 간단한 쿼리 실행
        result = await db.execute("SELECT 1")
        return {
            "status": "ok",
            "message": "데이터베이스 연결됨"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"데이터베이스 연결 오류: {str(e)}"
        }


@router.get("/redis", response_model=Dict[str, Any])
async def redis_health_check():
    """
    Redis 연결 상태를 확인합니다.
    """
    # TODO: 실제 Redis 연결 체크 로직 구현
    return {
        "status": "ok",
        "message": "Redis 연결됨"
    }


@router.get("/s3", response_model=Dict[str, Any])
async def s3_health_check():
    """
    S3(Minio) 연결 상태를 확인합니다.
    """
    # TODO: 실제 S3 연결 체크 로직 구현
    return {
        "status": "ok",
        "message": "S3 스토리지 연결됨"
    }


@router.get("/prefect", response_model=Dict[str, Any])
async def prefect_health_check():
    """
    Prefect 워크플로우 서버 연결 상태를 확인합니다.
    """
    # TODO: 실제 Prefect 연결 체크 로직 구현
    return {
        "status": "ok",
        "message": "Prefect 워크플로우 서버 연결됨"
    } 