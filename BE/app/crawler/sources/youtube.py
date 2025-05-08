# 여기에 유튜브 크롤러 코드 작성

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import googleapiclient.discovery
import googleapiclient.errors

class YouTubeCrawler:
    def __init__(self, api_key: Optional[str] = None):
        """
        :param api_key: YouTube Data API v3 키 (환경변수 또는 인자로 전달)
        """
        self.api_key = api_key or os.getenv('YOUTUBE_API_KEY')
        self.youtube = self.get_youtube_client(self.api_key)

    def get_youtube_client(self, api_key: str):
        if not api_key:
            raise ValueError("YouTube API 키가 필요합니다.")
        api_service_name = "youtube"
        api_version = "v3"
        return googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)

    def search_videos(
        self, query: str, max_results: int = 5,
        published_after: Optional[str] = None, published_before: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        검색어로 유튜브 영상을 검색(기간 필터 포함)하여 YoutubeVideos 모델 dict 리스트로 반환
        :param published_after: (선택) 시작일, RFC 3339 형식 (예: '2024-01-01T00:00:00Z')
        :param published_before: (선택) 종료일, RFC 3339 형식 (예: '2024-12-31T23:59:59Z')
        """
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "order": "relevance",
            "maxResults": max_results
        }
        if published_after:
            params["publishedAfter"] = published_after
        if published_before:
            params["publishedBefore"] = published_before

        response = self.youtube.search().list(**params).execute()
        videos = []
        for item in response.get('items', []):
            video_id = item.get('id', {}).get('videoId')
            snippet = item.get('snippet', {})
            channel_id = snippet.get('channelId')
            published_at = snippet.get('publishedAt')
            # 영상 상세 정보 추가 조회
            video_detail = self.youtube.videos().list(
                part="statistics,snippet",
                id=video_id
            ).execute()
            stats = video_detail['items'][0].get('statistics', {}) if video_detail['items'] else {}
            snippet_detail = video_detail['items'][0].get('snippet', {}) if video_detail['items'] else {}
            videos.append({
                'id': video_id,
                'channel_id': channel_id,
                'created_at': published_at,
                'like_count': int(stats.get('likeCount', 0)) if stats.get('likeCount') else None,
                'comment_count': int(stats.get('commentCount', 0)) if stats.get('commentCount') else None,
                'view_count': int(stats.get('viewCount', 0)) if stats.get('viewCount') else None,
                'updated_at': snippet_detail.get('publishedAt')
            })
        return videos

    def get_video_comments(self, video_id: str, max_comments: int = 100) -> List[Dict[str, Any]]:
        """
        특정 영상의 댓글을 YoutubeComments 모델 dict 리스트로 반환
        :return: [{id, video_id, text, created_at}, ...]
        """
        comments = []
        next_page_token = None
        fetched_count = 0
        while fetched_count < max_comments:
            max_batch = min(100, max_comments - fetched_count)
            response = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_batch,
                pageToken=next_page_token,
                textFormat="plainText"
            ).execute()
            items = response.get("items", [])
            for item in items:
                snippet = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                comment_id = item.get("snippet", {}).get("topLevelComment", {}).get("id")
                comment_text = snippet.get("textDisplay")
                published_at = snippet.get("publishedAt")
                if comment_id and comment_text:
                    comments.append({
                        "id": comment_id,
                        "video_id": video_id,
                        "text": comment_text,
                        "created_at": published_at
                    })
                    fetched_count += 1
                if fetched_count >= max_comments:
                    break
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
        return comments

    def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """
        채널 ID로 YoutubeChannels 모델 dict 반환
        :return: {id, name, subscriber_count, updated_at}
        """
        response = self.youtube.channels().list(
            part="snippet,statistics",
            id=channel_id
        ).execute()
        if not response['items']:
            return {}
        item = response['items'][0]
        snippet = item.get('snippet', {})
        statistics = item.get('statistics', {})
        return {
            'id': channel_id,
            'name': snippet.get('title'),
            'subscriber_count': int(statistics.get('subscriberCount', 0)) if statistics.get('subscriberCount') else None,
            'updated_at': snippet.get('publishedAt')
        }

    async def crawl(
        self, query: str, max_videos: int = 5, max_comments: int = 100,
        published_after: Optional[str] = None, published_before: Optional[str] = None
    ):
        """
        검색어로 유튜브 영상, 댓글, 채널 정보를 모두 수집하여 반환합니다.
        :return: {
            "videos": [...],  # YoutubeVideos 모델 dict 리스트
            "comments": [...],  # YoutubeComments 모델 dict 리스트
            "channels": [...]   # YoutubeChannels 모델 dict 리스트
        }
        """
        videos = self.search_videos(
            query, max_results=max_videos,
            published_after=published_after, published_before=published_before
        )
        all_comments = []
        channel_ids = set()
        for video in videos:
            video_id = video["id"]
            channel_id = video["channel_id"]
            channel_ids.add(channel_id)
            comments = self.get_video_comments(video_id, max_comments=max_comments)
            all_comments.extend(comments)
        channels = [self.get_channel_info(cid) for cid in channel_ids]
        return {
            "videos": videos,
            "comments": all_comments,
            "channels": channels
        }