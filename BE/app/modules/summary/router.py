from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date, timedelta, datetime
from collections import defaultdict

from app.core.db import get_db
from app.models import (
    Keywords, CollectedInstizPosts, CollectedYoutubeComments, CollectedTiktokComments,
    InstizPosts, YoutubeComments, TiktokComments,
    ContentAnalysis
)
from . import schemas

router = APIRouter()

PLATFORM_TABLES = {
    "instiz": (CollectedInstizPosts, InstizPosts),
    "youtube": (CollectedYoutubeComments, YoutubeComments),
    "tiktok": (CollectedTiktokComments, TiktokComments),
}

SOURCE_MAP = {
    "youtube_comments": "youtube",
    "tiktok_comments": "tiktok",
    "instiz_posts": "instiz"
}


@router.get("/overview", response_model=schemas.SummaryOverviewResponse)
async def get_summary_overview(
    product: str = Query(...),
    from_: date = Query(..., alias="from"),
    to: date = Query(...),
    db: Session = Depends(get_db)
):
    from_dt = datetime.combine(from_, datetime.min.time())
    to_dt = datetime.combine(to, datetime.max.time())
    duration = (to - from_).days + 1
    prev_from_dt = from_dt - timedelta(days=duration)
    prev_to_dt = from_dt - timedelta(seconds=1)

    # 1. 키워드 조회
    keyword_obj = db.execute(select(Keywords).where(Keywords.keyword == product)).scalar_one_or_none()
    if not keyword_obj:
        raise HTTPException(status_code=404, detail="Keyword not found")
    keyword_id = keyword_obj.id

    current_sources = []
    prev_sources = []

    platforms = ["youtube", "tiktok", "instiz"]  # ← 항상 전체 플랫폼 포함

    for plat in platforms:
        collected_model, original_model = PLATFORM_TABLES[plat]
        source_type = original_model.__tablename__

        # 수집된 ID 조회
        collected_ids = db.execute(
            select(collected_model).where(collected_model.keyword_id == keyword_id)
        ).scalars().all()
        id_field = getattr(collected_model, list(collected_model.__table__.columns)[0].name)
        original_ids = [getattr(col, id_field.name) for col in collected_ids]

        # 현재 기간 콘텐츠
        current_data = db.execute(
            select(original_model).where(
                original_model.id.in_(original_ids),
                original_model.is_analyzed == True,
                original_model.created_at.between(from_dt, to_dt)
            )
        ).scalars().all()
        current_sources += [(source_type, src) for src in current_data]

        # 이전 기간 콘텐츠
        prev_data = db.execute(
            select(original_model).where(
                original_model.id.in_(original_ids),
                original_model.is_analyzed == True,
                original_model.created_at.between(prev_from_dt, prev_to_dt)
            )
        ).scalars().all()
        prev_sources += [(source_type, src) for src in prev_data]

    # 4. 분석 결과 조회
    def fetch_analysis(sources):
        analysis_results = []
        for source_type, src in sources:
            records = db.execute(
                select(ContentAnalysis)
                .where(
                    ContentAnalysis.source_type == source_type,
                    ContentAnalysis.source_id == str(src.id)
                )
            ).scalars().all()
            if records:
                analysis_results.append((source_type, src.created_at.date(), records))
        return analysis_results

    current_analysis = fetch_analysis(current_sources)
    prev_analysis = fetch_analysis(prev_sources)

    # 5. SummaryChange 계산
    def count_sentiments(analysis):
        pos = neu = neg = 0
        for _, _, records in analysis:
            scores = [r.sentiment_id for r in records]
            avg = sum(scores) / len(scores)
            if avg == 1.0:
                pos += 1
            elif avg == 0.0:
                neg += 1
            else:
                neu += 1
        return pos, neu, neg

    pos_now, neu_now, neg_now = count_sentiments(current_analysis)
    pos_prev, neu_prev, neg_prev = count_sentiments(prev_analysis)
    total_now = pos_now + neu_now + neg_now
    total_prev = pos_prev + neu_prev + neg_prev

    def percent(v, total):
        return f"{(v / total * 100):.2f}%" if total else "0.00%"

    def delta(curr, prev):
        return f"{((curr - prev) / prev * 100):+.2f}%" if prev else "+0.00%"

    summary_change = schemas.SummaryChange(
        positive_change=percent(pos_now, total_now),
        positive_delta=delta(pos_now, pos_prev),
        negative_change=percent(neg_now, total_now),
        negative_delta=delta(neg_now, neg_prev),
        total_change=f"{total_now}개",
        total_delta=delta(total_now, total_prev)
    )

    # 6. sentiment_distribution
    distribution = defaultdict(lambda: {"positive": 0, "neutral": 0, "negative": 0})
    for source_type, _, records in current_analysis:
        scores = [r.sentiment_id for r in records]
        avg = sum(scores) / len(scores)
        label = (
            "positive" if avg == 1.0 else
            "negative" if avg == 0.0 else
            "neutral"
        )
        platform_key = SOURCE_MAP.get(source_type, "unknown")
        distribution[platform_key][label] += 1
        distribution["overall"][label] += 1

    sentiment_distribution = {
        key: schemas.SentimentDistributionItem(**value)
        for key, value in distribution.items()
    }

    # 7. sentiment_trend
    trend_map = defaultdict(lambda: {"positive": 0, "neutral": 0, "negative": 0})
    for _, created_date, records in current_analysis:
        scores = [r.sentiment_id for r in records]
        avg = sum(scores) / len(scores)
        label = (
            "positive" if avg == 1.0 else
            "negative" if avg == 0.0 else
            "neutral"
        )
        trend_map[created_date][label] += 1

    sentiment_trend = [
        schemas.SentimentTrendItem(date=str(day), **counts)
        for day, counts in sorted(trend_map.items())
    ]

    return schemas.SummaryOverviewResponse(
        summary_change=summary_change,
        sentiment_distribution=sentiment_distribution,
        sentiment_trend=sentiment_trend
    )
