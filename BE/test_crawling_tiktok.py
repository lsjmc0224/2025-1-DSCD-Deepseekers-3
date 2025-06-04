import asyncio
from datetime import datetime

from app.models import Keywords
from app.crawler.repositories import CrawlingRepository
from app.crawler.sources.tiktok import TikTokCrawler
from app.core.db import SessionLocal


async def main():
    db = SessionLocal()

    try:
        keyword_obj = db.query(Keywords).first()
        if not keyword_obj:
            print("❌ 키워드 테이블에 데이터가 없습니다.")
            return

        start_date = "2024-10-01"
        end_date = "2024-10-31"

        print(f"🔍 TikTok 크롤링 시작: '{keyword_obj.keyword}' ({start_date} ~ {end_date})")

        crawler = TikTokCrawler()
        repo = CrawlingRepository(db)

        # 1. 영상 수집
        video_data = await crawler.crawl(keyword=keyword_obj, start_date=start_date, end_date=end_date)
        print(f"🎬 영상 크롤링 완료: {len(video_data)}건")
        if not video_data:
            return

        # 2. 영상 저장 후 반드시 커밋
        video_result = repo.create_tiktok_videos(video_data)
        print(f"✅ 영상 저장 완료 - 새 영상: {video_result['videos_saved']}, 수집 기록: {video_result['video_collections_saved']}")

        # ⚠ 영상이 저장되지 않으면 댓글 저장도 실패하므로, 영상 먼저 커밋
        db.commit()  # 여기 꼭 필요!

        # 3. 댓글 수집 및 저장
        total_comments = 0
        for video in video_data:
            video_id = video["id"]
            comment_data = await crawler.crawl_comments(video_id)

            for comment in comment_data:
                comment["keyword_id"] = video["keyword_id"]
                comment["collected_at"] = video["collected_at"]

            result = repo.create_tiktok_comments(comment_data)
            print(f"💬 댓글 저장 - video_id={video_id}, 새 댓글: {result['comments_saved']}, 수집 기록: {result['comment_collections_saved']}")
            total_comments += result["comments_saved"]

        print(f"✅ 전체 댓글 저장 완료: {total_comments}건")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())  # ✅ 이거 꼭 추가해야 main()이 실행됩니다.
