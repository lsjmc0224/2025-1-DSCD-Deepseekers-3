from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date, datetime
from collections import Counter, defaultdict

from openai import OpenAI
from app.core.config import settings  # settings 불러오기

from app.core.db import get_db
from app.models import (
    Keywords, CollectedInstizPosts, CollectedYoutubeComments, CollectedTiktokComments,
    InstizPosts, YoutubeComments, TiktokComments,
    ContentAnalysis, Aspects
)
from . import schemas

SOURCE_MAP = {
    "instiz_posts": "커뮤니티",
    "youtube_comments": "유튜브",
    "tiktok_comments": "틱톡"
}

PLATFORM_TABLES = {
    "instiz": (CollectedInstizPosts, InstizPosts),
    "youtube": (CollectedYoutubeComments, YoutubeComments),
    "tiktok": (CollectedTiktokComments, TiktokComments),
}


def generate_summary(contents: list[str], positive_keywords: list[str], negative_keywords: list[str], product: str) -> str:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    reviews_text = "\n".join(contents[:100])
    prompt = f"""
당신은 고객 리뷰 분석 전문가입니다. 아래는 최근 일주일간 '{product}'에 대한 사용자 리뷰 텍스트들입니다. 이 리뷰들을 종합 분석하여 전반적인 소비자 반응을 간결하고 자연스럽게 요약해 주세요.
---

🔸 제품 이름: {product}

🔸 긍정적으로 자주 언급된 키워드:
{', '.join(positive_keywords) if positive_keywords else '없음'}

🔸 부정적으로 자주 언급된 키워드:
{', '.join(negative_keywords) if negative_keywords else '없음'}

🔸 사용자 리뷰 (최대 100개):
{reviews_text}

---

✅ 분석 요약 (소비자들이 이 제품을 어떻게 평가하는지, 어떤 점을 칭찬하고 어떤 점을 비판했는지 중심으로 3문장으로 요약 작성해 주세요):
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "너는 고객 리뷰 분석 전문가야."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[OpenAI 오류] {e}")
        return "리뷰 요약을 생성하는 데 실패했습니다."

router = APIRouter()

PLATFORM_TABLES = {
    "instiz": (CollectedInstizPosts, InstizPosts),
    "youtube": (CollectedYoutubeComments, YoutubeComments),
    "tiktok": (CollectedTiktokComments, TiktokComments),
}


@router.get("/overview", response_model=schemas.SentimentOverviewResponse)
async def get_sentiment_overview(
    product: str = Query(...),
    from_: date = Query(..., alias="from"),
    to: date = Query(...),
    db: Session = Depends(get_db)
):
    from_dt = datetime.combine(from_, datetime.min.time())
    to_dt = datetime.combine(to, datetime.max.time())

    # 1. 키워드 ID
    keyword_obj = db.execute(select(Keywords).where(Keywords.keyword == product)).scalar_one_or_none()
    if not keyword_obj:
        raise HTTPException(status_code=404, detail="Keyword not found")
    keyword_id = keyword_obj.id

    # 2. 전체 플랫폼에서 콘텐츠 수집
    source_type_to_ids = defaultdict(list)
    all_contents = []

    for platform, (collected_model, original_model) in PLATFORM_TABLES.items():
        source_type = original_model.__tablename__
        collected_rows = db.execute(
            select(collected_model).where(collected_model.keyword_id == keyword_id)
        ).scalars().all()
        id_field = getattr(collected_model, list(collected_model.__table__.columns)[0].name)
        content_ids = [getattr(row, id_field.name) for row in collected_rows]

        contents = db.execute(
            select(original_model).where(
                original_model.id.in_(content_ids),
                original_model.is_analyzed == True,
                original_model.created_at.between(from_dt, to_dt)
            )
        ).scalars().all()

        all_contents.extend(contents)
        for content in contents:
            source_type_to_ids[source_type].append(str(content.id))

    if not all_contents:
        return schemas.SentimentOverviewResponse(
            summary="해당 기간 동안 분석된 콘텐츠가 없습니다.",
            positive_keywords=[],
            negative_keywords=[],
            attribute_sentiment=[]
        )


    # 3. 분석 결과 추출
    all_analysis = db.execute(
        select(ContentAnalysis, Aspects.name)
        .join(Aspects, ContentAnalysis.aspect_id == Aspects.id)
        .where(
            ContentAnalysis.source_type.in_(source_type_to_ids.keys()),
            ContentAnalysis.source_id.in_(
                [sid for sids in source_type_to_ids.values() for sid in sids]
            )
        )
    ).all()

    # 4. 키워드 추출
    positive_counter = Counter()
    negative_counter = Counter()
    attribute_sentiment_map = defaultdict(lambda: {"긍정": 0, "부정": 0})

    for analysis, aspect_name in all_analysis:
        if analysis.sentiment_id == 1:
            positive_counter[analysis.evidence_keywords] += 1
            attribute_sentiment_map[aspect_name]["긍정"] += 1
        elif analysis.sentiment_id == 0:
            negative_counter[analysis.evidence_keywords] += 1
            attribute_sentiment_map[aspect_name]["부정"] += 1

    # 5. 결과 정리
    positive_keywords = [kw for kw, _ in positive_counter.most_common(10)]
    negative_keywords = [kw for kw, _ in negative_counter.most_common(10)]

    attribute_sentiment = [
        schemas.AttributeSentimentItem(
            name=aspect,
            긍정=counts["긍정"],
            부정=counts["부정"]
        )
        for aspect, counts in attribute_sentiment_map.items()
    ]

    # 6. 요약 생성
    sentences = [getattr(c, "text", getattr(c, "content", "")) for c in all_contents]
    summary_text = generate_summary(
        contents=sentences,
        positive_keywords=positive_keywords,
        negative_keywords=negative_keywords,
        product=product
    )

    return schemas.SentimentOverviewResponse(
        summary=summary_text,
        positive_keywords=positive_keywords,
        negative_keywords=negative_keywords,
        attribute_sentiment=attribute_sentiment
    )


@router.get("/details", response_model=schemas.SentimentDetailsResponse)
async def get_sentiment_details(
    product: str = Query(...),
    from_: date = Query(..., alias="from"),
    to: date = Query(...),
    top: int = Query(10),
    db: Session = Depends(get_db)
):
    from_dt = datetime.combine(from_, datetime.min.time())
    to_dt = datetime.combine(to, datetime.max.time())

    # 1. 키워드 확인
    keyword_obj = db.execute(
        select(Keywords).where(Keywords.keyword == product)
    ).scalar_one_or_none()

    if not keyword_obj:
        raise HTTPException(status_code=404, detail="Keyword not found")

    keyword_id = keyword_obj.id
    content_data = []

    # 2. 모든 플랫폼에서 수집 → 분석 여부 True + 기간 조건 충족
    for _, (collected_model, original_model) in PLATFORM_TABLES.items():
        source_type = original_model.__tablename__

        collected = db.execute(
            select(collected_model).where(collected_model.keyword_id == keyword_id)
        ).scalars().all()

        id_field = getattr(collected_model, list(collected_model.__table__.columns)[0].name)
        ids = [getattr(row, id_field.name) for row in collected]

        originals = db.execute(
            select(original_model).where(
                original_model.id.in_(ids),
                original_model.is_analyzed == True,
                original_model.created_at.between(from_dt, to_dt)
            )
        ).scalars().all()

        for content in originals:
            content_data.append((source_type, content))

    if not content_data:
        return schemas.SentimentDetailsResponse(
            positive=schemas.SentimentDetailsSection(summary="해당 기간에 분석된 댓글이 없습니다.", comments=[]),
            negative=schemas.SentimentDetailsSection(summary="해당 기간에 분석된 댓글이 없습니다.", comments=[])
        )

    # 3. 분석 결과 연결
    id_grouped = defaultdict(list)
    for source_type, content in content_data:
        id_grouped[source_type].append(str(content.id))

    analysis_map = defaultdict(list)
    for source_type, ids in id_grouped.items():
        analyses = db.execute(
            select(ContentAnalysis).where(
                ContentAnalysis.source_type == source_type,
                ContentAnalysis.source_id.in_(ids)
            )
        ).scalars().all()
        for a in analyses:
            analysis_map[(a.source_type, a.source_id)].append(a)

    # 4. likes 기준 상위 top% 필터링
    scored_data = []
    for source_type, content in content_data:
        likes = getattr(content, "like_count", None)
        if likes is not None:
            scored_data.append((source_type, content, likes))

    if not scored_data:
        raise HTTPException(status_code=400, detail="likes 값이 없는 데이터입니다.")

    # 상위 top%
    scored_data.sort(key=lambda x: x[2], reverse=True)
    cutoff = max(1, int(len(scored_data) * top / 100))
    top_data = scored_data[:cutoff]

    positive_group, negative_group = [], []

    for source_type, content, likes in top_data:
        key = (source_type, str(content.id))
        if key in analysis_map:
            sentiment_scores = [a.sentiment_id for a in analysis_map[key]]
            avg_score = sum(sentiment_scores) / len(sentiment_scores)
            if avg_score == 1.0:
                positive_group.append((source_type, content))
            elif avg_score == 0.0:
                negative_group.append((source_type, content))

    # 5. 최신 5개 댓글
    def build_comments(group: list, label: str) -> list[schemas.CommentItem]:
        sorted_group = sorted(group, key=lambda x: x[1].created_at, reverse=True)
        return [
            schemas.CommentItem(
                id=f"{source_type}-{content.id}",
                text=getattr(content, "text", getattr(content, "content", "")),
                date=content.created_at,
                sentiment=label,
                source=SOURCE_MAP.get(source_type, source_type),
                likes=getattr(content, "like_count", 0)
            )
            for source_type, content in sorted_group[:5]
        ]

    pos_comments = build_comments(positive_group, "positive")
    neg_comments = build_comments(negative_group, "negative")

    # 6. 요약 생성
    pos_texts = [c.text for c in pos_comments]
    neg_texts = [c.text for c in neg_comments]

    pos_summary = generate_summary(contents=pos_texts, positive_keywords=[], negative_keywords=[], product=product)
    neg_summary = generate_summary(contents=neg_texts, positive_keywords=[], negative_keywords=[], product=product)

    return schemas.SentimentDetailsResponse(
        positive=schemas.SentimentDetailsSection(summary=pos_summary, comments=pos_comments),
        negative=schemas.SentimentDetailsSection(summary=neg_summary, comments=neg_comments)
    )