# test_youtube_crawling.py

import asyncio
from datetime import datetime

from app.core.db import SessionLocal
from app.models import Keywords
from app.crawler.repositories import CrawlingRepository
from app.crawler.sources.youtube import YouTubeCrawler


async def main():
    db = SessionLocal()

    try:
        # ✅ 1. 테스트용 키워드 선택
        keyword_obj = db.query(Keywords).first()
        if not keyword_obj:
            print("❌ [ERROR] 키워드 테이블에 데이터가 없습니다.")
            return

        # ✅ 2. 크롤링 대상 기간 지정 (YYYYMMDD)
        starttime = "20241001"
        endtime = "20241031"

        print(f"\n🔍 YouTube 크롤링 시작: '{keyword_obj.keyword}' | {starttime} ~ {endtime}")
        crawler = YouTubeCrawler()

        # ✅ 3. 크롤링 실행
        result = await crawler.crawl(
            keyword=keyword_obj,
            max_videos=5,
            max_comments=20,
            published_after=starttime,
            published_before=endtime
        )

        videos = result["videos"]
        comments = result["comments"]
        channels = result["channels"]

        print(f"📺 영상 수집 완료: {len(videos)}건")
        print(f"💬 댓글 수집 완료: {len(comments)}건")
        print(f"📡 채널 수집 완료: {len(channels)}건")

        if not videos:
            print("⚠️ 영상이 없어 저장을 생략합니다.")
            return

        # ✅ 4. 저장 수행
        repo = CrawlingRepository(db)
        saved_counts = repo.create_youtube_data(
            channels=channels,
            videos=videos,
            comments=comments
        )

        # ✅ 5. 저장 실패 시 처리
        if saved_counts is None:
            print("❌ [ERROR] DB 저장 실패로 인해 저장 결과를 출력하지 않습니다.")
            return

        print("\n💾 DB 저장 결과:")
        for k, v in saved_counts.items():
            print(f" - {k}: {v}")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
