# app/scripts/dummy_data.py

from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from app.core.db import SessionLocal
from app.models import *


def insert_dummy_data(db: Session):
    # 💥 초기화
    db.query(ContentAnalyses).delete()
    db.query(CollectedYoutubeComments).delete()
    db.query(CollectedTiktokComments).delete()
    db.query(CollectedInstizComments).delete()
    db.query(InstizComments).delete()
    db.query(YoutubeComments).delete()
    db.query(TiktokComments).delete()
    db.query(YoutubeVideos).delete()
    db.query(InstizPosts).delete()
    db.query(TiktokVideos).delete()
    db.query(YoutubeChannels).delete()
    db.query(Keywords).delete()
    db.query(AnalysisLogs).delete()
    db.query(Aspects).delete()
    db.query(Sentiments).delete()
    db.commit()

    now = datetime.now(timezone.utc)

    # 1. 키워드
    kw1 = Keywords(keyword="편의점 디저트")
    kw2 = Keywords(keyword="편의점 도시락")

    # 2. 유튜브 채널
    yt_channel1 = YoutubeChannels(
        id="UC123456789",
        name="맛있는 유튜버",
        subscriber_count=150000,
        updated_at=now
    )

    # 3. 틱톡 영상
    tt_video1 = TiktokVideos(
        id="tt987654321",
        title="요즘 핫한 편의점 디저트🍰",
        video_url="https://www.tiktok.com/@user/video/987654321",
        created_at=now - timedelta(days=1),
        updated_at=now
    )

    # 4. 인스티즈 게시글
    instiz_post1 = InstizPosts(
        content="편의점 도시락 진짜 맛있다 ㄹㅇ ㅠㅠ",
        view_count=1234,
        like_count=56,
        comment_count=8,
        post_url="https://www.instiz.net/article/12345",
        created_at=now - timedelta(days=2),
        updated_at=now
    )

    db.add_all([kw1, kw2, yt_channel1, tt_video1, instiz_post1])
    db.commit()
    db.refresh(kw1)
    db.refresh(kw2)
    db.refresh(instiz_post1)

    print("✅ Keywords, YoutubeChannels, TiktokVideos, InstizPosts 더미 데이터 삽입 완료")

    # 5. 유튜브 영상
    yt_video1 = YoutubeVideos(
        id="ytvid001",
        channel_id=yt_channel1.id,
        created_at=now - timedelta(days=5),
        like_count=1200,
        comment_count=150,
        view_count=50000,
        updated_at=now
    )
    db.add(yt_video1)
    db.commit()
    db.refresh(yt_video1)

    # 6. 유튜브 댓글
    yt_comment1 = YoutubeComments(
        id="ytcom001",
        video_id=yt_video1.id,
        text="이 영상 보니까 당장 사러 가고 싶음 ㅋㅋ",
        created_at=now - timedelta(days=4)
    )

    # 7. 틱톡 댓글
    tt_comment1 = TiktokComments(
        id="ttcom001",
        video_id=tt_video1.id,
        text="진짜 편의점 미쳤다 요즘 ㅠㅠ",
        reply_count=0,
        user_id="user_tt_001",
        nickname="먹짱",
        parent_comment_id=None,
        is_reply=False,
        created_at=now - timedelta(days=3)
    )

    # 8. 인스티즈 댓글
    instiz_comment1 = InstizComments(
        post_id=instiz_post1.id,
        text="ㅇㅈ 진짜 요즘 편의점 도시락 개쩔",
        created_at=now - timedelta(days=2)
    )

    db.add_all([yt_comment1, tt_comment1, instiz_comment1])
    db.commit()
    db.refresh(yt_comment1)
    db.refresh(tt_comment1)
    db.refresh(instiz_comment1)

    print("✅ YoutubeVideos, YoutubeComments, TiktokComments, InstizComments 더미 데이터 삽입 완료")

    # 9. Collected 매핑
    collected_yt = CollectedYoutubeComments(
        comment_id=yt_comment1.id,
        keyword_id=kw1.id,
        collected_at=now
    )
    collected_tt = CollectedTiktokComments(
        comment_id=tt_comment1.id,
        keyword_id=kw1.id,
        collected_at=now
    )
    collected_instiz = CollectedInstizComments(
        comment_id=instiz_comment1.id,
        keyword_id=kw2.id,
        collected_at=now
    )
    db.add_all([collected_yt, collected_tt, collected_instiz])
    db.commit()
    print("✅ Collected 유튜브/틱톡/인스티즈 댓글 키워드 매핑 더미 데이터 삽입 완료")

    # 10. 분석 로그 및 감성 분석 결과
    log1 = AnalysisLogs(started_at=now - timedelta(minutes=10), finished_at=now)
    aspect1 = Aspects(name="맛")
    aspect2 = Aspects(name="식감")
    sentiment_pos = Sentiments(label="긍정", polarity=1)
    sentiment_neg = Sentiments(label="부정", polarity=2)
    db.add_all([log1, aspect1, aspect2, sentiment_pos, sentiment_neg])
    db.commit()
    db.refresh(log1)
    db.refresh(aspect1)
    db.refresh(aspect2)
    db.refresh(sentiment_pos)
    db.refresh(sentiment_neg)

    analysis1 = ContentAnalyses(
        analysis_log_id=log1.id,
        source_type="youtube",
        source_id=yt_video1.id,
        sentence="진짜 편의점 디저트 너무 맛있어요!",
        aspect_id=aspect1.id,
        sentiment_id=sentiment_pos.id,
        evidence_keywords="맛있,편의점"
    )
    analysis2 = ContentAnalyses(
        analysis_log_id=log1.id,
        source_type="instiz",
        source_id=str(instiz_post1.id),
        sentence="밥은 맛있었는데 식감이 좀 별로였음",
        aspect_id=aspect2.id,
        sentiment_id=sentiment_neg.id,
        evidence_keywords="식감,별로"
    )
    db.add_all([analysis1, analysis2])
    db.commit()
    print("✅ AnalysisLogs, Aspects, Sentiments, ContentAnalyses 더미 데이터 삽입 완료")


def main():
    db = SessionLocal()
    try:
        insert_dummy_data(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
