from typing import List, Dict, Any
from .sources.youtube import YouTubeCrawler
from .sources.instiz import InstizCrawler
from .sources.tiktok import TikTokCrawler

class CrawlerService:
    def __init__(self):
        self.youtube_crawler = YouTubeCrawler()
        self.instiz_crawler = InstizCrawler()
        self.tiktok_crawler = TikTokCrawler()

    async def crawl_youtube(self, query: str) -> List[Dict[str, Any]]:
        # TODO: Implement YouTube crawling
        pass

    async def crawl_instiz(self, board: str) -> List[Dict[str, Any]]:
        # TODO: Implement Instiz crawling
        pass

    async def crawl_tiktok(self, hashtag: str) -> List[Dict[str, Any]]:
        # TODO: Implement TikTok crawling
        pass 