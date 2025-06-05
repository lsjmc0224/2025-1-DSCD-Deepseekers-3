# test_instiz_crawling.py

import asyncio
from datetime import datetime

from app.core.db import SessionLocal
from app.models import Keywords
from app.crawler.repositories import CrawlingRepository
from app.crawler.sources.instiz import InstizCrawler


async def main():
    db = SessionLocal()

    try:
        # ✅ 1. keyword 더미 데이터 조회
        keyword_obj = db.query(Keywords).first()
        if not keyword_obj:
            print("❌ 키워드 테이블에 데이터가 없습니다.")
            return

        # ✅ 2. 크롤링 범위 설정 (2024년 10월 한 달)
        starttime = "20241001"
        endtime = "20241031"

        print(f"🔍 '{keyword_obj.keyword}' 키워드로 크롤링 시작: {starttime} ~ {endtime}")
        crawler = InstizCrawler()
        crawled_data = await crawler.crawl(keyword=keyword_obj, starttime=starttime, endtime=endtime)

        print(f"✅ 크롤링 완료: {len(crawled_data)}건")

        if not crawled_data:
            return

        # ✅ 3. 저장
        repo = CrawlingRepository(db)
        saved_count = repo.create_instiz_posts(crawled_data)

        print(f"✅ DB 저장 완료: {saved_count}건")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
