import asyncio
from datetime import datetime
from app.core.db import SessionLocal
from app.models import Keywords
from app.crawler.service import CrawlerService


async def run_direct_crawl_test():
    db = SessionLocal()
    try:
        keyword_text = "스웨덴젤리"

        # 기존 키워드 존재 확인
        keyword_obj = db.query(Keywords).filter_by(keyword=keyword_text).first()

        if keyword_obj:
            print(f"[SKIP] 이미 존재하는 키워드: {keyword_text}")
        else:
            # 새 키워드 추가
            print(f"[LOG] 신규 키워드 추가: {keyword_text}")
            keyword_obj = Keywords(keyword=keyword_text, searched_at=datetime.now())
            db.add(keyword_obj)
            db.commit()
            db.refresh(keyword_obj)

        # ✅ 크롤링 실행은 공통적으로 keyword_obj 사용
        print(f"[LOG] 크롤링 시작: {keyword_text}")
        service = CrawlerService()

        # ✅ 날짜 한 쌍만 지정
        start_date = "2025-02-04"
        end_date = "2025-02-14"

        # ✅ 형식 맞게 자동 할당
        youtube_period = {
            "starttime": start_date.replace("-", ""),
            "endtime": end_date.replace("-", "")
        }

        instiz_period = {
            "starttime": start_date.replace("-", ""),
            "endtime": end_date.replace("-", "")
        }

        tiktok_period = {
            "start_date": start_date,
            "end_date": end_date
        }

        result = await service.crawl_all(
            keyword_obj=keyword_obj,
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
