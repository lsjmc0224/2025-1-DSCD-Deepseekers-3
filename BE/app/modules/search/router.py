from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db, SessionLocal
from app.models import Keywords
from . import schemas
from app.crawler.service import CrawlerService
import time
from typing import List
from datetime import datetime

router = APIRouter()

@router.post("/keyword", response_model=schemas.SearchResult)
async def search_keyword(query: schemas.SearchQuery):
    db = SessionLocal()
    try:
        print(f"[LOG] 키워드 검색 요청: {query.keyword}")
        # 1. 키워드 존재 여부 확인
        keyword_obj = db.query(Keywords).filter_by(keyword=query.keyword).first()
        if keyword_obj:
            print(f"[LOG] 이미 존재하는 키워드: {query.keyword}")
            return schemas.SearchResult(
                keyword=query.keyword,
                results=[],
                total_count=0,
                search_time=0.0
            )

        # 2. 키워드 새로 추가
        print(f"[LOG] 신규 키워드 추가: {query.keyword}")
        new_keyword = Keywords(keyword=query.keyword, searched_at = datetime.now())
        db.add(new_keyword)
        db.commit()
        db.refresh(new_keyword)

        # 3. 크롤링 서비스 실행
        print(f"[LOG] 크롤링 서비스 시작: {query.keyword}")
        service = CrawlerService()
        start = time.time()
        # 기간 예시 (최근 한 달)
        youtube_period = {"starttime": "20241001", "endtime": "20241031"}
        instiz_period = {"starttime": "20241001", "endtime": "20241031"}
        tiktok_period = {"start_date": "2024-10-01", "end_date": "2024-10-31"}
        result = await service.crawl_all(
            keyword_obj=new_keyword,
            youtube_period=youtube_period,
            instiz_period=instiz_period,
            tiktok_period=tiktok_period
        )
        elapsed = time.time() - start
        print(f"[LOG] 크롤링 서비스 완료: {query.keyword} (소요 시간: {elapsed:.2f}초)")

        # 크롤링 실패 시
        if result.get("status") == "fail":
            print(f"[ERROR] 크롤링 실패: {result.get('message', '크롤링 실패')}")
            raise HTTPException(status_code=500, detail=result.get("message", "크롤링 실패"))

        print(f"[LOG] 전체 완료: {query.keyword}")
        return schemas.SearchResult(
            keyword=query.keyword,
            results=[result],
            total_count=1,
            search_time=elapsed
        )
    except Exception as e:
        print(f"[ERROR] 예외 발생: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get("/history", response_model=List[schemas.SearchHistory])
async def get_search_history():
    # TODO: Implement search history retrieval
    pass 