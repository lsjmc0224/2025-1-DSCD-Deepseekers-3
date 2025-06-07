from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date, datetime
from collections import defaultdict

from app.core.db import get_db
from app.models import (
    Keywords, CollectedYoutubeVideos, YoutubeVideos, YoutubeComments, ContentAnalysis
)
from . import schemas

router = APIRouter()


@router.get("/videos", response_model=schemas.VideoListResponse)
async def get_videos(
    product: str = Query(...),
    from_: date = Query(..., alias="from"),
    to: date = Query(...),
    db: Session = Depends(get_db)
):
    from_dt = datetime.combine(from_, datetime.min.time())
    to_dt = datetime.combine(to, datetime.max.time())

    # 1. 키워드 확인
    keyword = db.execute(
        select(Keywords).where(Keywords.keyword == product)
    ).scalar_one_or_none()

    if not keyword:
        raise HTTPException(status_code=404, detail="Keyword not found")

    keyword_id = keyword.id

    # 2. 수집된 영상 ID 확인
    collected = db.execute(
        select(CollectedYoutubeVideos).where(CollectedYoutubeVideos.keyword_id == keyword_id)
    ).scalars().all()
    video_ids = [col.video_id for col in collected]

    if not video_ids:
        return {"videos": []}

    # 3. 해당 기간 내 유튜브 영상 조회
    videos = db.execute(
        select(YoutubeVideos).where(
            YoutubeVideos.id.in_(video_ids),
            YoutubeVideos.created_at.between(from_dt, to_dt)
        )
    ).scalars().all()

    if not videos:
        return {"videos": []}

    video_id_set = {video.id for video in videos}

    # 4. 유튜브 댓글 조회
    comments = db.execute(
        select(YoutubeComments).where(YoutubeComments.video_id.in_(video_id_set))
    ).scalars().all()

    comment_map = defaultdict(list)
    for comment in comments:
        comment_map[comment.video_id].append(comment)

    # 5. content_analysis 분석 결과 조회
    comment_ids = [str(c.id) for c in comments]

    analyses = db.execute(
        select(ContentAnalysis).where(
            ContentAnalysis.source_type == "youtube_comments",
            ContentAnalysis.source_id.in_(comment_ids)
        )
    ).scalars().all()

    analysis_map = defaultdict(list)
    for a in analyses:
        analysis_map[a.source_id].append(a.sentiment_id)

    # 6. 감성 집계: 댓글별 평균 후 영상별 집계
    video_sentiments = defaultdict(lambda: {"positive": 0, "neutral": 0, "negative": 0})

    for comment in comments:
        sentiments = analysis_map.get(str(comment.id), [])
        if not sentiments:
            continue
        avg = sum(sentiments) / len(sentiments)
        if avg == 1.0:
            label = "positive"
        elif avg == 0.0:
            label = "negative"
        else:
            label = "neutral"
        video_sentiments[comment.video_id][label] += 1

    # 7. 응답 구성
    response = []
    for video in videos:
        sentiment = video_sentiments.get(video.id, {"positive": 0, "neutral": 0, "negative": 0})
        response.append(schemas.VideoItem(
            id=video.id,
            title=video.title,
            thumbnail_url=video.thumbnail_url,  # ✅ 실제 DB 저장값 사용
            views=video.view_count,
            likes=video.like_count,
            comments=video.comment_count,
            publish_date=video.created_at.isoformat(),
            is_short=(video.video_type == "short"),
            sentiments=schemas.VideoSentiment(**sentiment)
        ))

    return {"videos": response}
