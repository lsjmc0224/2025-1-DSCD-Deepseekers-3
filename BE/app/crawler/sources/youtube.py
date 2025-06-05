import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import googleapiclient.discovery
from dotenv import load_dotenv

from app.models import Keywords


class YouTubeCrawler:
    def __init__(self, api_key: Optional[str] = None):
        dotenv_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'
        )
        load_dotenv(dotenv_path)
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.youtube = self.get_youtube_client(self.api_key)

    def get_youtube_client(self, api_key: str):
        if not api_key:
            raise ValueError("YouTube API 키가 필요합니다.")
        return googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)

    def yyyymmdd_to_rfc3339(self, yyyymmdd: str, end: bool = False) -> str:
        dt = datetime.strptime(yyyymmdd, "%Y%m%d")
        if end:
            dt = dt.replace(hour=23, minute=59, second=59)
        else:
            dt = dt.replace(hour=0, minute=0, second=0)
        return dt.isoformat("T") + "Z"

    def search_videos(
        self,
        keyword: Keywords,
        max_results: int,
        published_after: Optional[str],
        published_before: Optional[str],
        video_duration: Optional[str],  # ✅ "short", "medium", "long"
    ) -> List[Dict[str, Any]]:
        params = {
            "part": "snippet",
            "q": keyword.keyword,
            "type": "video",
            "order": "relevance",
            "maxResults": max_results,
            "videoDuration": video_duration or "any"  # ✅ 여기에 포함
        }
        if published_after:
            params["publishedAfter"] = self.yyyymmdd_to_rfc3339(published_after)
        if published_before:
            params["publishedBefore"] = self.yyyymmdd_to_rfc3339(published_before, end=True)

        response = self.youtube.search().list(**params).execute()
        videos = []

        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]
            channel_id = snippet["channelId"]
            published_at = snippet["publishedAt"]

            video_detail = self.youtube.videos().list(part="statistics,snippet", id=video_id).execute()
            video_info = video_detail["items"][0] if video_detail["items"] else {}

            stats = video_info.get("statistics", {})
            snippet_detail = video_info.get("snippet", {})

            videos.append({
                "id": video_id,
                "channel_id": channel_id,
                "created_at": published_at,
                "keyword_id": keyword.id,
                "collected_at": datetime.now(),
                "like_count": int(stats.get("likeCount", 0)) if "likeCount" in stats else None,
                "comment_count": int(stats.get("commentCount", 0)) if "commentCount" in stats else None,
                "view_count": int(stats.get("viewCount", 0)) if "viewCount" in stats else None,
                "updated_at": snippet_detail.get("publishedAt"),
                "video_type": video_duration,  # ✅ "short", "medium", "long"
            })

        return videos

    def get_video_comments(self, keyword: Keywords, video_id: str, max_comments: int = 100) -> List[Dict[str, Any]]:
        comments = []
        next_page_token = None
        fetched = 0

        while fetched < max_comments:
            max_batch = min(100, max_comments - fetched)
            response = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_batch,
                pageToken=next_page_token,
                textFormat="plainText"
            ).execute()

            for item in response.get("items", []):
                snippet = item["snippet"]["topLevelComment"]["snippet"]
                comment_id = item["snippet"]["topLevelComment"]["id"]
                comments.append({
                    "id": comment_id,
                    "video_id": video_id,
                    "keyword_id": keyword.id,
                    "content": snippet.get("textDisplay", ""),
                    "created_at": snippet.get("publishedAt"),
                })
                fetched += 1
                if fetched >= max_comments:
                    break

            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break

        return comments

    def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        response = self.youtube.channels().list(part="snippet,statistics", id=channel_id).execute()
        if not response["items"]:
            return {}
        item = response["items"][0]
        return {
            "id": channel_id,
            "name": item["snippet"]["title"],
            "subscriber_count": int(item["statistics"].get("subscriberCount", 0)),
            "updated_at": item["snippet"]["publishedAt"],
        }

    async def crawl(
        self,
        keyword: Keywords,
        max_videos: int = 5,
        max_comments: int = 100,
        published_after: Optional[str] = None,
        published_before: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        all_videos = []
        all_comments = []
        channel_ids = set()

        for duration in ["short", "medium", "long"]:
            videos = self.search_videos(
                keyword=keyword,
                max_results=max_videos,
                published_after=published_after,
                published_before=published_before,
                video_duration=duration,  # ✅ 문자열 전달
            )
            for video in videos:
                video["keyword_id"] = keyword.id
                all_videos.append(video)
                channel_ids.add(video["channel_id"])

                comments = self.get_video_comments(keyword, video["id"], max_comments=max_comments)
                all_comments.extend(comments)

        channels = [self.get_channel_info(cid) for cid in channel_ids]

        return {
            "videos": all_videos,
            "comments": all_comments,
            "channels": channels,
        }
