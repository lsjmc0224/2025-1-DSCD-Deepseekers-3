import asyncio
from datetime import datetime
from app.core.db import SessionLocal
from app.models import Keywords
from app.crawler.service import CrawlerService


async def run_direct_crawl_test():
    db = SessionLocal()
    try:
        keyword_text = "밤티라미수"

        # 기존 키워드 존재 확인
        keyword_obj = db.query(Keywords).filter_by(keyword=keyword_text).first()
        if keyword_obj:
            print(f"[SKIP] 이미 존재하는 키워드: {keyword_text}")
            return

        # 새 키워드 추가
        print(f"[LOG] 신규 키워드 추가: {keyword_text}")
        new_keyword = Keywords(keyword=keyword_text, searched_at=datetime.now())
        db.add(new_keyword)
        db.commit()
        db.refresh(new_keyword)

        # 크롤링 실행
        service = CrawlerService()
        youtube_period = {"starttime": "20241001", "endtime": "20241031"}
        instiz_period = {"starttime": "20241001", "endtime": "20241031"}
        tiktok_period = {"start_date": "2024-10-01", "end_date": "2024-10-31"}

        print(f"[LOG] 크롤링 시작: {keyword_text}")
        result = await service.crawl_all(
            keyword_obj=new_keyword,
            youtube_period=youtube_period,
            instiz_period=instiz_period,
            tiktok_period=tiktok_period
        )

        if result.get("status") == "fail":
            raise Exception(f"크롤링 실패: {result.get('message')}")

        print(f"[SUCCESS] 크롤링 완료: {keyword_text}")
        print(f"[RESULT] {result}")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] 테스트 중 예외 발생: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(run_direct_crawl_test())
