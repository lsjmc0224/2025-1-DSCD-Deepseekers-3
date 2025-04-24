"""
YouTube 데이터 수집 모듈

이 모듈은 YouTube API를 사용하여 비디오 메타데이터, 댓글, 트랜스크립트 등을 
수집하는 기능을 제공합니다. youtube-comment-downloader를 사용하여 API 할당량 제한 없이
댓글을 수집합니다.
"""
import os
import re
import json
import uuid
import logging
import asyncio
import aiohttp
import backoff
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
from functools import partial

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_RECENT, SORT_BY_POPULAR

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 환경 변수에서 YouTube API 키 가져오기
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')

# 데이터 저장 경로
DATA_DIR = Path("data/youtube")
DATA_DIR.mkdir(parents=True, exist_ok=True)


def generate_request_id() -> str:
    """
    요청 ID를 생성합니다.
    
    Returns:
        생성된 요청 ID
    """
    return str(uuid.uuid4())


def extract_video_id(url_or_id: str) -> Optional[str]:
    """
    YouTube URL 또는 ID에서 비디오 ID를 추출합니다.
    
    Args:
        url_or_id: YouTube URL 또는 비디오 ID
        
    Returns:
        추출된 비디오 ID 또는 None
    """
    # URL인 경우 파싱
    if url_or_id.startswith('http'):
        parsed_url = urlparse(url_or_id)
        
        # youtube.com 형식
        if 'youtube.com' in parsed_url.netloc:
            if '/watch' in parsed_url.path:
                return parse_qs(parsed_url.query).get('v', [None])[0]
            elif '/shorts/' in parsed_url.path:
                return parsed_url.path.split('/shorts/')[1].split('/')[0]
        # youtu.be 형식
        elif 'youtu.be' in parsed_url.netloc:
            return parsed_url.path.strip('/')
    
    # ID 형식 확인 (일반적으로 11자리 영숫자)
    elif re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    
    return None


@backoff.on_exception(backoff.expo, 
                     (HttpError, aiohttp.ClientError), 
                     max_tries=5,
                     on_backoff=lambda details: logger.warning(f"요청 실패, 재시도 중... (시도: {details['tries']})"))
async def get_video_metadata(video_id: str) -> Dict[str, Any]:
    """
    YouTube 비디오의 메타데이터를 가져옵니다.
    
    Args:
        video_id: YouTube 비디오 ID
        
    Returns:
        비디오 메타데이터
    """
    if not YOUTUBE_API_KEY:
        logger.error("YOUTUBE_API_KEY가 설정되지 않았습니다.")
        return {}
    
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        # 비디오 세부 정보 가져오기
        video_response = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=video_id
        ).execute()
        
        if not video_response.get('items'):
            logger.warning(f"비디오 ID {video_id}에 대한 정보를 찾을 수 없습니다.")
            return {}
        
        # 채널 정보 가져오기
        video_data = video_response['items'][0]
        channel_id = video_data['snippet']['channelId']
        
        channel_response = youtube.channels().list(
            part='snippet,statistics',
            id=channel_id
        ).execute()
        
        channel_data = channel_response['items'][0] if channel_response.get('items') else {}
        
        # 타임스탬프를 날짜/시간으로 변환
        published_at = video_data['snippet']['publishedAt']
        pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
        
        # 메타데이터 구성
        metadata = {
            'video_id': video_id,
            'title': video_data['snippet']['title'],
            'description': video_data['snippet']['description'],
            'published_at': pub_date.isoformat(),
            'channel_id': channel_id,
            'channel_title': video_data['snippet']['channelTitle'],
            'channel_subscriber_count': channel_data.get('statistics', {}).get('subscriberCount'),
            'view_count': video_data['statistics'].get('viewCount'),
            'like_count': video_data['statistics'].get('likeCount'),
            'comment_count': video_data['statistics'].get('commentCount'),
            'duration': video_data['contentDetails']['duration'],
            'tags': video_data['snippet'].get('tags', []),
            'category_id': video_data['snippet'].get('categoryId'),
            'thumbnail_url': video_data['snippet']['thumbnails'].get('high', {}).get('url'),
            'collected_at': datetime.now(timezone.utc).isoformat()
        }
        
        return metadata
    
    except HttpError as e:
        logger.error(f"YouTube API 요청 중 오류 발생: {e}")
        raise
    except Exception as e:
        logger.error(f"비디오 메타데이터 가져오기 중 오류 발생: {e}")
        return {}


async def get_video_comments(video_id: str, max_comments: int = 100, sort_by: str = 'time') -> List[Dict[str, Any]]:
    """
    YouTube 비디오의 댓글을 가져옵니다.
    youtube-comment-downloader를 사용하여 API 할당량 제한 없이 댓글을 수집합니다.
    
    Args:
        video_id: YouTube 비디오 ID
        max_comments: 가져올 최대 댓글 수
        sort_by: 정렬 방식 ('time' 또는 'popular')
        
    Returns:
        댓글 목록
    """
    logger.info(f"비디오 {video_id}에서 최대 {max_comments}개의 댓글을 가져옵니다.")
    
    # youtube-comment-downloader 초기화
    downloader = YoutubeCommentDownloader()
    
    # 정렬 옵션 설정
    sort_option = SORT_BY_POPULAR if sort_by == 'popular' else SORT_BY_RECENT
    
    try:
        comments = []
        # 비동기 환경에서 youtube-comment-downloader 실행 (이는 동기 라이브러리이므로 실행 방식에 주의)
        loop = asyncio.get_event_loop()
        
        # 댓글 수집 함수를 partial로 래핑하여 실행
        get_comments_func = partial(downloader.get_comments, video_id, sort_by=sort_option)
        
        # 비동기 실행을 위해 run_in_executor 사용
        def collect_comments():
            result = []
            for comment in get_comments_func():
                result.append({
                    'comment_id': comment.get('cid', ''),
                    'text': comment.get('text', ''),
                    'author': comment.get('author', ''),
                    'author_id': comment.get('author_id', ''),
                    'like_count': comment.get('votes', 0),
                    'published_at': comment.get('time', ''),
                    'is_reply': bool(comment.get('parent', '')),
                    'parent_id': comment.get('parent', ''),
                    'collected_at': datetime.now(timezone.utc).isoformat()
                })
                if len(result) >= max_comments:
                    break
            return result
        
        comments = await loop.run_in_executor(None, collect_comments)
        
        logger.info(f"비디오 {video_id}에서 {len(comments)}개의 댓글을 수집했습니다.")
        return comments
    
    except Exception as e:
        logger.error(f"댓글 가져오기 중 오류 발생: {e}")
        return []


async def get_video_transcript(video_id: str) -> List[Dict[str, Any]]:
    """
    유튜브 동영상의 자막(트랜스크립트)을 가져옵니다.

    Args:
        video_id: 유튜브 동영상 ID

    Returns:
        자막 목록. 각 항목은 텍스트, 시작 시간, 지속 시간을 포함
    """
    try:
        # 비동기 환경에서 youtube_transcript_api 실행 (동기식 API)
        loop = asyncio.get_event_loop()
        get_transcript_func = partial(YouTubeTranscriptApi.get_transcript, 
                                      video_id, 
                                      languages=['ko', 'en'])
        
        # 비동기 실행을 위해 run_in_executor 사용
        transcript = await loop.run_in_executor(None, get_transcript_func)
        
        logger.info(f"동영상 {video_id}에서 {len(transcript)}개의 자막 항목을 수집했습니다.")
        return transcript
    except NoTranscriptFound:
        logger.warning(f"동영상 {video_id}에 자막이 없습니다.")
        return []
    except TranscriptsDisabled:
        logger.warning(f"동영상 {video_id}의 자막이 비활성화되었습니다.")
        return []
    except Exception as e:
        logger.error(f"동영상 {video_id}의 자막을 가져오는 중 오류 발생: {str(e)}")
        return []


async def search_videos_by_keywords(keywords: List[str], max_results: int = 10) -> List[str]:
    """
    키워드를 기반으로 YouTube 비디오를 검색합니다.
    
    Args:
        keywords: 검색 키워드 목록
        max_results: 반환할 최대 결과 수
        
    Returns:
        검색된 비디오 ID 목록
    """
    if not YOUTUBE_API_KEY:
        logger.error("YOUTUBE_API_KEY가 설정되지 않았습니다.")
        return []
    
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        video_ids = []
        
        for keyword in keywords:
            logger.info(f"키워드 '{keyword}'로 비디오 검색 중...")
            
            # 키워드로 비디오 검색
            search_response = youtube.search().list(
                q=keyword,
                part='id',
                maxResults=max_results,
                type='video',
                relevanceLanguage='ko',
                safeSearch='none',
                order='relevance'
            ).execute()
            
            # 검색 결과에서 비디오 ID 추출
            for item in search_response.get('items', []):
                if item['id']['kind'] == 'youtube#video':
                    video_ids.append(item['id']['videoId'])
            
            if len(video_ids) >= max_results:
                break
        
        logger.info(f"총 {len(video_ids)}개의 비디오 검색됨")
        return video_ids[:max_results]
    
    except HttpError as e:
        logger.error(f"YouTube API 요청 중 오류 발생: {e}")
        return []
    except Exception as e:
        logger.error(f"비디오 검색 중 오류 발생: {e}")
        return []


async def get_channel_videos(channel_id: str, max_results: int = 10) -> List[str]:
    """
    특정 채널의 최신 비디오를 가져옵니다.
    
    Args:
        channel_id: YouTube 채널 ID
        max_results: 반환할 최대 결과 수
        
    Returns:
        채널 비디오 ID 목록
    """
    if not YOUTUBE_API_KEY:
        logger.error("YOUTUBE_API_KEY가 설정되지 않았습니다.")
        return []
    
    try:
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        # 채널의 업로드 재생목록 ID 가져오기
        channel_response = youtube.channels().list(
            part='contentDetails',
            id=channel_id
        ).execute()
        
        if not channel_response.get('items'):
            logger.warning(f"채널 ID {channel_id}에 대한 정보를 찾을 수 없습니다.")
            return []
        
        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        # 재생목록의 비디오 가져오기
        playlist_response = youtube.playlistItems().list(
            part='snippet',
            playlistId=uploads_playlist_id,
            maxResults=max_results
        ).execute()
        
        # 재생목록에서 비디오 ID 추출
        video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_response.get('items', [])]
        
        logger.info(f"채널 {channel_id}에서 {len(video_ids)}개의 비디오를 가져왔습니다.")
        return video_ids
    
    except HttpError as e:
        logger.error(f"YouTube API 요청 중 오류 발생: {e}")
        return []
    except Exception as e:
        logger.error(f"채널 비디오 가져오기 중 오류 발생: {e}")
        return []


async def collect_youtube_data(
    video_id_or_url: str,
    max_comments: int = 100,
    comment_sort: str = 'time',
    save_to_file: bool = True,
    output_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    YouTube 비디오의 데이터(메타데이터, 댓글, 자막)를 수집합니다.
    
    Args:
        video_id_or_url: YouTube 비디오 ID 또는 URL
        max_comments: 수집할 최대 댓글 수
        comment_sort: 댓글 정렬 방식 ('time' 또는 'popular')
        save_to_file: 파일에 저장할지 여부
        output_path: 결과를 저장할 경로 (None이면 기본 경로 사용)
        
    Returns:
        수집된 데이터
    """
    # 비디오 ID 추출
    video_id = extract_video_id(video_id_or_url)
    if not video_id:
        logger.error(f"유효한 YouTube 비디오 ID 또는 URL이 아닙니다: {video_id_or_url}")
        return {}
    
    logger.info(f"비디오 {video_id}의 데이터 수집 시작")
    request_id = generate_request_id()
    
    # 비동기로 메타데이터, 댓글, 자막 동시에 가져오기
    metadata_task = asyncio.create_task(get_video_metadata(video_id))
    comments_task = asyncio.create_task(get_video_comments(video_id, max_comments, comment_sort))
    transcript_task = asyncio.create_task(get_video_transcript(video_id))
    
    # 모든 태스크 완료 대기
    metadata = await metadata_task
    comments = await comments_task
    transcript = await transcript_task
    
    # 수집된 데이터 통합
    collected_data = {
        'request_id': request_id,
        'video_id': video_id,
        'metadata': metadata,
        'comments': comments,
        'transcript': transcript,
        'collection_time': datetime.now(timezone.utc).isoformat()
    }
    
    # 파일에 저장
    if save_to_file:
        if output_path is None:
            output_path = DATA_DIR / f"video_{video_id}_{request_id}.json"
        else:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(collected_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"수집된 데이터가 {output_path}에 저장되었습니다.")
    
    statistics = {
        'video_id': video_id,
        'metadata_collected': bool(metadata),
        'comments_count': len(comments),
        'transcript_items_count': len(transcript),
        'collection_time': collected_data['collection_time']
    }
    
    logger.info(f"비디오 {video_id} 데이터 수집 완료: {statistics}")
    return collected_data 