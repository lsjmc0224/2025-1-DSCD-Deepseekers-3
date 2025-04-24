#!/usr/bin/env python
"""
YouTube 데이터 수집 서비스

YouTube API를 사용하여 동영상, 댓글, 메타데이터를 수집하는 서비스입니다.
비동기 수집 작업을 지원하며, 수집 상태를 추적할 수 있습니다.
"""

import os
import re
import json
import uuid
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

import httpx
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from fastapi import BackgroundTasks

from app.core.config import settings
from app.db.redis_client import redis_client

# 로깅 설정
logger = logging.getLogger(__name__)

# YouTube API 클라이언트 설정
YOUTUBE_API_KEY = settings.YOUTUBE_API_KEY

# 수집 작업 상태 저장을 위한 Redis 키 접두사
COLLECTION_STATUS_PREFIX = "youtube_collection_status:"


def generate_request_id() -> str:
    """
    유니크한 요청 ID를 생성합니다.
    
    Returns:
        str: 생성된 요청 ID
    """
    return str(uuid.uuid4())


async def get_collection_status(request_id: str) -> Dict[str, Any]:
    """
    YouTube 데이터 수집 작업의 상태를 조회합니다.
    
    Args:
        request_id: 수집 요청 ID
        
    Returns:
        Dict[str, Any]: 수집 작업 상태 정보
    """
    status_key = f"{COLLECTION_STATUS_PREFIX}{request_id}"
    
    # Redis에서 상태 조회
    status_data = await redis_client.get(status_key)
    
    if not status_data:
        return {
            "status": "not_found",
            "message": f"요청 ID '{request_id}'에 대한 수집 작업을 찾을 수 없습니다.",
            "request_id": request_id
        }
    
    try:
        status = json.loads(status_data)
        return status
    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "상태 정보를 파싱하는 중 오류가 발생했습니다.",
            "request_id": request_id
        }


async def update_collection_status(
    request_id: str, 
    status: str, 
    progress: int = 0, 
    message: str = "", 
    result: Optional[Dict[str, Any]] = None
) -> None:
    """
    YouTube 데이터 수집 작업의 상태를 업데이트합니다.
    
    Args:
        request_id: 수집 요청 ID
        status: 상태 (pending, in_progress, completed, error)
        progress: 진행률 (0-100)
        message: 상태 메시지
        result: 수집 결과 데이터
    """
    status_key = f"{COLLECTION_STATUS_PREFIX}{request_id}"
    
    status_data = {
        "request_id": request_id,
        "status": status,
        "progress": progress,
        "message": message,
        "updated_at": datetime.now().isoformat(),
    }
    
    if result:
        status_data["result"] = result
    
    # Redis에 상태 저장 (24시간 유지)
    await redis_client.set(
        status_key, 
        json.dumps(status_data), 
        expire=86400
    )


async def initialize_youtube_api():
    """
    YouTube API 클라이언트를 초기화합니다.
    
    Returns:
        googleapiclient.discovery.Resource: YouTube API 클라이언트
    """
    try:
        youtube_client = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        return youtube_client
    except Exception as e:
        logger.error(f"YouTube API 클라이언트 초기화 중 오류 발생: {str(e)}")
        raise


async def search_videos_by_keywords(
    keywords: List[str], 
    max_results: int = 5,
) -> List[str]:
    """
    키워드 목록으로 YouTube 동영상을 검색합니다.
    
    Args:
        keywords: 검색할 키워드 목록
        max_results: 키워드별 최대 결과 수
        
    Returns:
        List[str]: 검색된 동영상 ID 목록
    """
    youtube = await initialize_youtube_api()
    video_ids = []
    
    try:
        for keyword in keywords:
            search_response = youtube.search().list(
                q=keyword,
                part='id,snippet',
                maxResults=max_results,
                type='video',
                relevanceLanguage='ko'
            ).execute()
            
            for item in search_response.get('items', []):
                if item['id']['kind'] == 'youtube#video':
                    video_ids.append(item['id']['videoId'])
        
        return video_ids
    
    except Exception as e:
        logger.error(f"YouTube 동영상 검색 중 오류 발생: {str(e)}")
        return []


async def get_video_metadata(video_id: str) -> Optional[Dict[str, Any]]:
    """
    YouTube 동영상의 메타데이터를 가져옵니다.
    
    Args:
        video_id: 동영상 ID
        
    Returns:
        Optional[Dict[str, Any]]: 동영상 메타데이터
    """
    youtube = await initialize_youtube_api()
    
    try:
        video_response = youtube.videos().list(
            part='snippet,statistics,contentDetails',
            id=video_id
        ).execute()
        
        if not video_response.get('items'):
            logger.warning(f"동영상 ID '{video_id}'에 대한 메타데이터를 찾을 수 없습니다.")
            return None
        
        item = video_response['items'][0]
        snippet = item['snippet']
        statistics = item['statistics']
        
        return {
            "video_id": video_id,
            "title": snippet.get('title', ''),
            "description": snippet.get('description', ''),
            "published_at": snippet.get('publishedAt', ''),
            "channel_id": snippet.get('channelId', ''),
            "channel_title": snippet.get('channelTitle', ''),
            "tags": snippet.get('tags', []),
            "thumbnail_url": snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
            "view_count": int(statistics.get('viewCount', 0)),
            "like_count": int(statistics.get('likeCount', 0)),
            "comment_count": int(statistics.get('commentCount', 0)),
            "duration": item.get('contentDetails', {}).get('duration', '')
        }
    
    except Exception as e:
        logger.error(f"동영상 '{video_id}' 메타데이터 가져오기 중 오류 발생: {str(e)}")
        return None


async def get_video_comments(
    video_id: str, 
    max_comments: int = 100, 
    sort: str = 'time'
) -> List[Dict[str, Any]]:
    """
    YouTube 동영상의 댓글을 가져옵니다.
    
    Args:
        video_id: 동영상 ID
        max_comments: 최대 댓글 수
        sort: 정렬 방식 ('time' 또는 'relevance')
        
    Returns:
        List[Dict[str, Any]]: 댓글 목록
    """
    youtube = await initialize_youtube_api()
    comments = []
    
    try:
        # 댓글 정렬 방식 설정
        order = 'time' if sort == 'time' else 'relevance'
        
        # 댓글 스레드 가져오기
        next_page_token = None
        while len(comments) < max_comments:
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=min(100, max_comments - len(comments)),
                order=order,
                pageToken=next_page_token
            )
            response = request.execute()
            
            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']
                
                comments.append({
                    "comment_id": item['id'],
                    "text_original": comment.get('textOriginal', ''),
                    "author_display_name": comment.get('authorDisplayName', ''),
                    "author_profile_image_url": comment.get('authorProfileImageUrl', ''),
                    "author_channel_id": comment.get('authorChannelId', {}).get('value', ''),
                    "like_count": comment.get('likeCount', 0),
                    "published_at": comment.get('publishedAt', ''),
                    "updated_at": comment.get('updatedAt', '')
                })
            
            next_page_token = response.get('nextPageToken')
            if not next_page_token or len(comments) >= max_comments:
                break
        
        return comments[:max_comments]
    
    except Exception as e:
        logger.error(f"동영상 '{video_id}' 댓글 가져오기 중 오류 발생: {str(e)}")
        return []


async def collect_video_data(
    video_id: str, 
    max_comments: int = 100
) -> Optional[Dict[str, Any]]:
    """
    단일 YouTube 동영상의 데이터를 수집합니다.
    
    Args:
        video_id: 동영상 ID
        max_comments: 최대 댓글 수
        
    Returns:
        Optional[Dict[str, Any]]: 수집된 동영상 데이터
    """
    # 메타데이터 가져오기
    metadata = await get_video_metadata(video_id)
    
    if not metadata:
        return None
    
    # 댓글 가져오기
    comments = await get_video_comments(video_id, max_comments)
    
    # 결과 취합
    video_data = {
        **metadata,
        "comments": comments,
        "comments_count": len(comments),
        "collected_at": datetime.now().isoformat()
    }
    
    return video_data


async def process_collection(
    request_id: str,
    video_ids: List[str],
    max_comments: int = 100
) -> None:
    """
    백그라운드 작업으로 실행되는 YouTube 데이터 수집 처리 함수입니다.
    
    Args:
        request_id: 수집 요청 ID
        video_ids: 수집할 동영상 ID 목록
        max_comments: 동영상당 최대 댓글 수
    """
    # 초기 상태 업데이트
    await update_collection_status(
        request_id=request_id,
        status="in_progress",
        progress=0,
        message=f"{len(video_ids)}개 동영상 수집 시작"
    )
    
    videos = []
    total_comments = 0
    error_count = 0
    
    # 각 동영상 처리
    for index, video_id in enumerate(video_ids):
        try:
            # 진행 상태 업데이트
            progress = int((index / len(video_ids)) * 100)
            await update_collection_status(
                request_id=request_id,
                status="in_progress",
                progress=progress,
                message=f"동영상 '{video_id}' 수집 중 ({index+1}/{len(video_ids)})"
            )
            
            # 동영상 데이터 수집
            video_data = await collect_video_data(video_id, max_comments)
            
            if video_data:
                videos.append(video_data)
                total_comments += len(video_data.get("comments", []))
                logger.info(f"동영상 '{video_id}' 수집 완료 (댓글: {len(video_data.get('comments', []))}개)")
            else:
                error_count += 1
                logger.warning(f"동영상 '{video_id}' 수집 실패")
        
        except Exception as e:
            error_count += 1
            logger.error(f"동영상 '{video_id}' 처리 중 오류 발생: {str(e)}")
    
    # 최종 상태 업데이트
    result = {
        "videos": videos,
        "total_videos": len(videos),
        "total_comments": total_comments,
        "failed_videos": error_count,
        "collection_timestamp": datetime.now().isoformat()
    }
    
    await update_collection_status(
        request_id=request_id,
        status="completed",
        progress=100,
        message=f"수집 완료: {len(videos)}개 동영상, {total_comments}개 댓글, {error_count}개 실패",
        result=result
    )


async def collect_youtube_data(
    video_ids: List[str], 
    max_comments: int = 100,
    background_tasks: Optional[BackgroundTasks] = None
) -> Dict[str, Any]:
    """
    YouTube 동영상 데이터 수집 작업을 시작합니다.
    
    Args:
        video_ids: 수집할 동영상 ID 목록
        max_comments: 동영상당 최대 댓글 수
        background_tasks: FastAPI BackgroundTasks (비동기 작업용)
        
    Returns:
        Dict[str, Any]: 수집 작업 시작 결과
    """
    # 요청 ID 생성
    request_id = generate_request_id()
    
    # 초기 상태 저장
    await update_collection_status(
        request_id=request_id,
        status="pending",
        message=f"{len(video_ids)}개 동영상 수집 작업 대기 중"
    )
    
    # 백그라운드 작업으로 처리
    if background_tasks:
        background_tasks.add_task(
            process_collection,
            request_id=request_id,
            video_ids=video_ids,
            max_comments=max_comments
        )
    else:
        # 백그라운드 태스크가 제공되지 않으면 직접 비동기 태스크 생성
        asyncio.create_task(
            process_collection(
                request_id=request_id,
                video_ids=video_ids,
                max_comments=max_comments
            )
        )
    
    return {
        "request_id": request_id,
        "message": f"{len(video_ids)}개 동영상 수집 작업이 시작되었습니다.",
        "status": "pending"
    } 