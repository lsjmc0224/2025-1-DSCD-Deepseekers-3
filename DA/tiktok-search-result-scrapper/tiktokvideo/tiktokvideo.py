import jmespath
import json

from typing import Any, Dict, Iterator, Optional
from requests import Session, Response
from loguru import logger
from tiktokvideo.typing import SearchResult, Video

class TiktokVideo:
    BASE_URL: str = 'https://www.tiktok.com'
    API_URL: str = f'{BASE_URL}/api/search/general/full/'
    AID: int = 1988

    def __init__(
        self: 'TiktokVideo'
    ) -> None:
        self.__session: Session = Session()
    
    def __parse_video(
        self: 'TiktokVideo', 
        data: Dict[str, Any]
    ) -> Video:
        data: Dict[str, Any] = jmespath.search(
            """
            {
                video_id: item.id,
                desc: item.desc,
                create_time: item.createTime,
                duration: item.video.duration,
                digg_count: item.stats.diggCount,
                share_count: item.stats.shareCount,
                comment_count: item.stats.commentCount,
                play_count: item.stats.playCount,
                collect_count: item.stats.collectCount,
                is_ad: item.isAd
            }
            """,
            data
        )
        return Video(**data)
    
    def get_videos(
            self, 
            keyword: str, 
            offset: Optional[int] = 12, 
            page: Optional[int] = 1
            ) -> SearchResult:
        response: Response = self.__session.get(
            self.API_URL,
            params={
                'aid': 1988,
                'keyword': keyword,
                'offset': (page - 1) * offset,
                # 'device_type': 'web_h264',
                # 'from_page': 'search',
                # 'referer': 'https://www.google.com/',
                # 'root_referer': 'https://www.google.com/',
                # 'search_source': 'recom_search',
                # 'web_search_code': '%7B%22tiktok%22%3A%7B%22client_params_x%22%3A%7B%22search_engine%22%3A%7B%22ies_mt_user_live_video_card_use_libra%22%3A1%2C%22mt_search_general_user_live_card%22%3A1%7D%7D%2C%22search_server%22%3A%7B%7D%7D%7D',
            }
        )

        logger.info(f"API Response Status Code: {response.status_code}")
        logger.info(f"API Response Text (First 500 chars): {response.text[:500]}")

        # 응답 본문이 비어 있으면 예외 발생
        if not response.text.strip():
            raise Exception("TikTok API 응답이 비어 있습니다. 요청이 차단되었을 가능성이 높습니다.")

        try:
            data: Dict[str, Any] = response.json()
        except json.JSONDecodeError:
            raise Exception(f"API 응답이 JSON 형식이 아닙니다: {response.text[:500]}")

        videos = [self.__parse_video(item) for item in data.get('data', [])]

        return SearchResult(
            videos=videos,
            has_more=data.get('has_more', False),
            cursor=data.get('cursor', 0),
            keyword=keyword
        )

    
    def get_all_videos(
            self, 
            keyword: str, 
            offset: Optional[int] = 12
            ) -> SearchResult:
        page: int = 1
        all_videos = []
        while True:
            result = self.get_videos(keyword, offset, page)
            all_videos.extend(result.videos)
            
            if not result.has_more:
                break
            
            page += 1

        return SearchResult(
            videos=all_videos,
            has_more=False,
            cursor=0,
            keyword=keyword
        )
