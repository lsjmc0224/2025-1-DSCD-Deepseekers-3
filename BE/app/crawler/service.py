from typing import List, Dict, Any
from .sources.youtube import YouTubeCrawler
from .sources.instiz import InstizCrawler
from .sources.tiktok import TikTokCrawler
from app.crawler.repositories import CrawlingRepository
from app.core.db import SessionLocal
from app.models.Keywords import Keywords
from sqlalchemy.exc import SQLAlchemyError

class CrawlerService:
    def __init__(self):
        self.youtube_crawler = YouTubeCrawler()
        self.instiz_crawler = InstizCrawler()
        self.tiktok_crawler = TikTokCrawler()

    async def crawl_instiz(self, keyword_obj: Keywords, starttime: str, endtime: str) -> List[Dict[str, Any]]:
        return await self.instiz_crawler.crawl(keyword=keyword_obj, starttime=starttime, endtime=endtime)

    async def crawl_tiktok(self, keyword_obj: Keywords, start_date: str, end_date: str) -> Dict[str, Any]:
        return await self.tiktok_crawler.crawl(keyword=keyword_obj, start_date=start_date, end_date=end_date)

    async def crawl_all(self, keyword_obj: Keywords, youtube_period: Dict[str, str], instiz_period: Dict[str, str], tiktok_period: Dict[str, str]) -> Dict[str, Any]:
        """
        3개 플랫폼(YouTube, Instiz, TikTok) 크롤링 및 저장을 한 번에 수행.
        하나라도 실패하면 전체 롤백. 성공 시 완료 로그 반환.
        """
        db = SessionLocal()
        repo = CrawlingRepository(db)
        try:
            # 1. Instiz
            try:
                instiz_data = await self.instiz_crawler.crawl(
                    keyword=keyword_obj,
                    starttime=instiz_period["starttime"],
                    endtime=instiz_period["endtime"]
                )
                if not repo.create_instiz_posts(instiz_data):
                    raise Exception("Instiz 저장 실패")
            except Exception as e:
                db.rollback()
                return {"status": "fail", "message": f"[Instiz] 저장 실패: {str(e)}"}

            # 2. TikTok
            try:
                tiktok_data = await self.tiktok_crawler.crawl(
                    keyword=keyword_obj,
                    start_date=tiktok_period["start_date"],
                    end_date=tiktok_period["end_date"]
                )

                tiktok_videos = tiktok_data["videos"]
                tiktok_comments = tiktok_data["comments"]

                if tiktok_videos and not repo.create_tiktok_videos(tiktok_videos):
                    raise Exception("TikTok 영상 저장 실패")

                if tiktok_comments and not repo.create_tiktok_comments(tiktok_comments):
                    raise Exception("TikTok 댓글 저장 실패")

            except Exception as e:
                db.rollback()
                return {"status": "fail", "message": f"[TikTok] 저장 실패: {str(e)}"}

            # 3. YouTube
            try:
                yt_result = await self.youtube_crawler.crawl(
                    keyword=keyword_obj,
                    max_videos=20,
                    max_comments=100,
                    published_after=youtube_period["starttime"],
                    published_before=youtube_period["endtime"]
                )
                if not repo.create_youtube_data(
                    channels=yt_result["channels"],
                    videos=yt_result["videos"],
                    comments=yt_result["comments"]
                ):
                    raise Exception("YouTube 저장 실패")
            except Exception as e:
                db.rollback()
                return {"status": "fail", "message": f"[YouTube] 저장 실패: {str(e)}"}

            db.commit()
            return {"status": "success", "message": "✅ 모든 플랫폼 크롤링 및 저장이 성공적으로 완료되었습니다."}
        except Exception as e:
            db.rollback()
            return {"status": "fail", "message": f"[전체 실패] {str(e)}"}
        finally:
            db.close()
