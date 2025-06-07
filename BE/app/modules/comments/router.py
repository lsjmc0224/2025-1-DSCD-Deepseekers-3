from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from typing import List
from datetime import date, datetime

from app.core.db import get_db
from app.models import (
    Keywords,
    CollectedInstizPosts, CollectedTiktokComments, CollectedYoutubeComments,
    InstizPosts, TiktokComments, YoutubeComments,
    ContentAnalysis, Sentiments, Aspects
)
from . import schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.Comment])
async def get_comments(
    from_: date = Query(..., alias="from"),
    to: date = Query(...),
    keyword: str = Query(...),
    db: Session = Depends(get_db)
):
    # 1. 키워드 ID 조회
    keyword_obj = db.execute(
        select(Keywords).where(Keywords.keyword == keyword)
    ).scalar_one_or_none()

    if not keyword_obj:
        raise HTTPException(status_code=404, detail="Keyword not found")

    keyword_id = keyword_obj.id
    from_dt = datetime.combine(from_, datetime.min.time())
    to_dt = datetime.combine(to, datetime.max.time())

    # 2. 각 플랫폼의 수집 테이블에서 ID 추출
    instiz_ids = db.execute(
        select(CollectedInstizPosts.post_id)
        .where(CollectedInstizPosts.keyword_id == keyword_id)
    ).scalars().all()

    tiktok_ids = db.execute(
        select(CollectedTiktokComments.comment_id)
        .where(CollectedTiktokComments.keyword_id == keyword_id)
    ).scalars().all()

    youtube_ids = db.execute(
        select(CollectedYoutubeComments.comment_id)
        .where(CollectedYoutubeComments.keyword_id == keyword_id)
    ).scalars().all()

    results = []

    # 3-1. Instiz posts
    if instiz_ids:
        instiz_posts = db.execute(
            select(InstizPosts)
            .where(
                InstizPosts.id.in_(instiz_ids),
                InstizPosts.is_analyzed == True,
                InstizPosts.created_at.between(from_dt, to_dt)
            )
        ).scalars().all()

        for post in instiz_posts:
            analyses = db.execute(
                select(ContentAnalysis, Sentiments.label, Aspects.name)
                .join(Sentiments, Sentiments.id == ContentAnalysis.sentiment_id)
                .join(Aspects, Aspects.id == ContentAnalysis.aspect_id)
                .where(
                    ContentAnalysis.source_type == InstizPosts.__tablename__,
                    ContentAnalysis.source_id == str(post.id)
                )
            ).all()

            if not analyses:
                continue

            # 평균 감성 점수 계산
            sentiment_scores = [ca.sentiment_id for ca, _, _ in analyses]
            avg_score = sum(sentiment_scores) / len(sentiment_scores)

            if avg_score == 0.0:
                sentiment = "negative"
            elif avg_score == 1.0:
                sentiment = "positive"
            else:
                sentiment = "neutral"

            # 대표 분석 결과 하나 선택 (예: 첫 번째)
            ca, _, aspect_label = analyses[0]

            results.append(schemas.Comment(
                id=f"{InstizPosts.__tablename__}-{post.id}",
                text=post.content,
                date=post.created_at,
                sentiment=sentiment,
                source="인스티즈",
                likes=post.like_count if hasattr(post, "like_count") else None,
                attributes=[aspect_label],
                analysis=schemas.CommentAnalysis(
                    sentiment_score=round(avg_score, 2),
                    aspect=ca.evidence_keywords
                )
            ))

    # 3-2. TikTok comments
    if tiktok_ids:
        tiktok_comments = db.execute(
            select(TiktokComments)
            .where(
                TiktokComments.id.in_(tiktok_ids),
                TiktokComments.is_analyzed == True,
                TiktokComments.created_at.between(from_dt, to_dt)
            )
        ).scalars().all()

        for comment in tiktok_comments:
            analyses = db.execute(
                select(ContentAnalysis, Sentiments.label, Aspects.name)
                .join(Sentiments, Sentiments.id == ContentAnalysis.sentiment_id)
                .join(Aspects, Aspects.id == ContentAnalysis.aspect_id)
                .where(
                    ContentAnalysis.source_type == TiktokComments.__tablename__,
                    ContentAnalysis.source_id == str(comment.id)
                )
            ).all()

            if not analyses:
                continue

            sentiment_scores = [ca.sentiment_id for ca, _, _ in analyses]
            avg_score = sum(sentiment_scores) / len(sentiment_scores)

            if avg_score == 0.0:
                sentiment = "negative"
            elif avg_score == 1.0:
                sentiment = "positive"
            else:
                sentiment = "neutral"

            ca, _, aspect_label = analyses[0]

            results.append(schemas.Comment(
                id=f"{TiktokComments.__tablename__}-{comment.id}",
                text=comment.text,
                date=comment.created_at,
                sentiment=sentiment,
                source="틱톡",
                likes=comment.like_count if hasattr(comment, "like_count") else None,
                attributes=[aspect_label],
                analysis=schemas.CommentAnalysis(
                    sentiment_score=round(avg_score, 2),
                    aspect=ca.evidence_keywords
                )
            ))

    # 3-3. YouTube comments
    if youtube_ids:
        youtube_comments = db.execute(
            select(YoutubeComments)
            .where(
                YoutubeComments.id.in_(youtube_ids),
                YoutubeComments.is_analyzed == True,
                YoutubeComments.created_at.between(from_dt, to_dt)
            )
        ).scalars().all()

        for comment in youtube_comments:
            analyses = db.execute(
                select(ContentAnalysis, Sentiments.label, Aspects.name)
                .join(Sentiments, Sentiments.id == ContentAnalysis.sentiment_id)
                .join(Aspects, Aspects.id == ContentAnalysis.aspect_id)
                .where(
                    ContentAnalysis.source_type == YoutubeComments.__tablename__,
                    ContentAnalysis.source_id == str(comment.id)
                )
            ).all()

            if not analyses:
                continue

            sentiment_scores = [ca.sentiment_id for ca, _, _ in analyses]
            avg_score = sum(sentiment_scores) / len(sentiment_scores)

            if avg_score == 0.0:
                sentiment = "negative"
            elif avg_score == 1.0:
                sentiment = "positive"
            else:
                sentiment = "neutral"

            ca, _, aspect_label = analyses[0]

            results.append(schemas.Comment(
                id=f"{YoutubeComments.__tablename__}-{comment.id}",
                text=comment.text,
                date=comment.created_at,
                sentiment=sentiment,
                source="유튜브",
                likes=comment.like_count if hasattr(comment, "like_count") else None,
                attributes=[aspect_label],
                analysis=schemas.CommentAnalysis(
                    sentiment_score=round(avg_score, 2),
                    aspect=ca.evidence_keywords
                )
            ))

    return results
