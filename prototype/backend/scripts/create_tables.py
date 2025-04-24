#!/usr/bin/env python
"""
데이터베이스 테이블 생성 스크립트

사용법:
    python create_tables.py
"""

import os
import sys
import asyncio

# 상위 디렉토리를 경로에 추가하여 app 모듈 가져오기
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.db.base import get_metadata


async def create_tables():
    """
    모든 데이터베이스 테이블을 생성합니다.
    """
    engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), echo=True)
    
    print("데이터베이스 테이블 생성 중...")
    
    async with engine.begin() as conn:
        for metadata in get_metadata():
            await conn.run_sync(metadata.create_all)
    
    print("데이터베이스 테이블 생성 완료.")


if __name__ == "__main__":
    asyncio.run(create_tables()) 