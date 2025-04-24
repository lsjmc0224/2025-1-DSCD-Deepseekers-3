"""
데이터베이스 세션 관리

이 모듈은 SQLAlchemy 비동기 세션 생성과 관리를 담당합니다.
"""

from typing import AsyncGenerator, Optional
import logging

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# 로깅 설정
logger = logging.getLogger(__name__)

# 비동기 엔진 생성
engine = create_async_engine(
    settings.DATABASE_URI,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# 비동기 세션 생성
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False, 
    autocommit=False, 
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    의존성 주입을 위한 데이터베이스 세션 생성기
    
    이 함수는 FastAPI 엔드포인트에서 의존성으로 사용됩니다.
    컨텍스트 관리자로 세션을 관리하며, 요청 처리 후 자동으로 세션을 닫습니다.
    
    Yields:
        AsyncGenerator[AsyncSession, None]: 비동기 SQLAlchemy 세션
    """
    async with AsyncSessionLocal() as session:
        try:
            logger.debug("데이터베이스 세션 생성")
            yield session
        except Exception as e:
            logger.error(f"데이터베이스 세션 오류: {str(e)}")
            await session.rollback()
            raise
        finally:
            logger.debug("데이터베이스 세션 종료")


async def init_db() -> None:
    """
    데이터베이스 초기화
    
    이 함수는 애플리케이션 시작 시 데이터베이스 초기화 작업을 수행합니다.
    테이블 생성 및 초기 데이터 설정 등의 작업을 여기서 처리합니다.
    """
    logger.info("데이터베이스 초기화 중...")
    try:
        # 테이블 생성
        # async with engine.begin() as conn:
        #     # 개발 환경에서만 사용
        #     # from app.db.base import Base
        #     # await conn.run_sync(Base.metadata.drop_all)
        #     # await conn.run_sync(Base.metadata.create_all)
        
        # 초기 데이터 설정
        # await seed_data()
        
        logger.info("데이터베이스 초기화 완료")
    except Exception as e:
        logger.error(f"데이터베이스 초기화 오류: {str(e)}")
        raise


async def close_db() -> None:
    """
    데이터베이스 연결 종료
    
    이 함수는 애플리케이션 종료 시 데이터베이스 연결을 정리합니다.
    """
    logger.info("데이터베이스 연결 종료 중...")
    try:
        await engine.dispose()
        logger.info("데이터베이스 연결 종료 완료")
    except Exception as e:
        logger.error(f"데이터베이스 연결 종료 오류: {str(e)}")
        raise 