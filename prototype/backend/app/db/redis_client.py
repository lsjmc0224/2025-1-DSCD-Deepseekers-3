#!/usr/bin/env python
"""
Redis 클라이언트 모듈

이 모듈은 시스템 전체에서 사용되는 Redis 연결 및 작업을 관리합니다.
비동기 Redis 클라이언트를 제공하며, 상태 추적, 캐싱, 큐 등의 용도로 사용됩니다.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union

import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    """비동기 Redis 클라이언트 클래스"""
    
    def __init__(self):
        """Redis 클라이언트 초기화"""
        self._redis = None
        self._pool = None
    
    async def _get_redis(self) -> redis.Redis:
        """Redis 연결 가져오기"""
        if self._redis is None:
            try:
                # 연결 풀 생성
                self._pool = redis.ConnectionPool.from_url(
                    settings.REDIS_URI,
                    encoding="utf-8",
                    decode_responses=True
                )
                self._redis = redis.Redis(connection_pool=self._pool)
                # 연결 테스트
                await self._redis.ping()
                logger.info("Redis 서버에 연결되었습니다")
            except Exception as e:
                logger.error(f"Redis 연결 오류: {str(e)}")
                raise
        return self._redis
    
    async def get(self, key: str) -> Optional[str]:
        """
        Redis에서 값을 가져옵니다.
        
        Args:
            key: 가져올 데이터의 키
            
        Returns:
            문자열 값 또는 None
        """
        try:
            redis_client = await self._get_redis()
            return await redis_client.get(key)
        except Exception as e:
            logger.error(f"Redis get 오류: {str(e)}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: str, 
        expire: Optional[int] = None
    ) -> bool:
        """
        Redis에 값을 저장합니다.
        
        Args:
            key: 저장할 데이터의 키
            value: 저장할 데이터의 값
            expire: 만료 시간(초)
            
        Returns:
            성공 여부
        """
        try:
            redis_client = await self._get_redis()
            await redis_client.set(key, value)
            if expire:
                await redis_client.expire(key, expire)
            return True
        except Exception as e:
            logger.error(f"Redis set 오류: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Redis에서 키를 삭제합니다.
        
        Args:
            key: 삭제할 키
            
        Returns:
            성공 여부
        """
        try:
            redis_client = await self._get_redis()
            await redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete 오류: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Redis에 키가 존재하는지 확인합니다.
        
        Args:
            key: 확인할 키
            
        Returns:
            키 존재 여부
        """
        try:
            redis_client = await self._get_redis()
            return await redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists 오류: {str(e)}")
            return False
    
    async def hset(self, name: str, key: str, value: str) -> bool:
        """
        Redis 해시에 필드를 설정합니다.
        
        Args:
            name: 해시 이름
            key: 필드 이름
            value: 필드 값
            
        Returns:
            성공 여부
        """
        try:
            redis_client = await self._get_redis()
            await redis_client.hset(name, key, value)
            return True
        except Exception as e:
            logger.error(f"Redis hset 오류: {str(e)}")
            return False
    
    async def hget(self, name: str, key: str) -> Optional[str]:
        """
        Redis 해시에서 필드 값을 가져옵니다.
        
        Args:
            name: 해시 이름
            key: 필드 이름
            
        Returns:
            필드 값 또는 None
        """
        try:
            redis_client = await self._get_redis()
            return await redis_client.hget(name, key)
        except Exception as e:
            logger.error(f"Redis hget 오류: {str(e)}")
            return None
    
    async def hgetall(self, name: str) -> Dict[str, str]:
        """
        Redis 해시의 모든 필드와 값을 가져옵니다.
        
        Args:
            name: 해시 이름
            
        Returns:
            필드와 값의 딕셔너리
        """
        try:
            redis_client = await self._get_redis()
            return await redis_client.hgetall(name)
        except Exception as e:
            logger.error(f"Redis hgetall 오류: {str(e)}")
            return {}
    
    async def keys(self, pattern: str) -> List[str]:
        """
        패턴과 일치하는 모든 키를 가져옵니다.
        
        Args:
            pattern: 키 패턴
            
        Returns:
            일치하는 키 목록
        """
        try:
            redis_client = await self._get_redis()
            return await redis_client.keys(pattern)
        except Exception as e:
            logger.error(f"Redis keys 오류: {str(e)}")
            return []
    
    async def close(self) -> None:
        """Redis 연결을 종료합니다."""
        if self._redis:
            await self._redis.close()
            self._redis = None
        if self._pool:
            await self._pool.disconnect()
            self._pool = None


# 싱글톤 인스턴스 생성
redis_client = RedisClient()


async def init_redis() -> None:
    """Redis 연결을 초기화합니다."""
    await redis_client._get_redis()


async def close_redis() -> None:
    """Redis 연결을 종료합니다."""
    await redis_client.close() 