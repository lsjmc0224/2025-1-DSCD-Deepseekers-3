from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import *  # 각 테이블의 SQLAlchemy ORM 모델이 정의되어 있어야 함

# ⚠️ 실제 사용 환경에 맞게 수정
DATABASE_URL = "postgresql+psycopg2://postgres:newpassword123@localhost:5432/mydb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def insert_dummy_data():
    session = SessionLocal()

    try:
        now = datetime.utcnow()

        # 1. Keywords
        keyword = Keywords(keyword="딸기라떼", searched_at=now)
        session.add(keyword)
        session.flush()  # keyword.id 확보

        # 2. Youtube Channel
        channel = YoutubeChannels(id="UC123", name="테스트 채널", subscriber_count=10000, updated_at=now)
        session.add(channel)

        # 3. Youtube Video
        video = YoutubeVideos(
            id="vid123",
            channel_id=channel.id,
            keyword_id=keyword.id,
            video_type="Shorts",
            created_at=now - timedelta(days=1),
            like_count=100,
            comment_count=5,
            view_count=1000,
            updated_at=now
        )
        session.add(video)

        # 4. Youtube Comment
        comment = YoutubeComments(
            id="com123",
            video_id=video.id,
            text="정말 맛있어 보여요!",
            created_at=now
        )
        session.add(comment)

        # 5. CollectedYoutubeVideos / CollectedYoutubeComments
        session.add(CollectedYoutubeVideos(
            video_id=video.id,
            keyword_id=keyword.id,
            collected_at=now
        ))
        session.add(CollectedYoutubeComments(
            comment_id=comment.id,
            keyword_id=keyword.id,
            collected_at=now
        ))

        # 6. Instiz Post
        post = InstizPosts(
            content="이거 실화냐",
            view_count=1500,
            like_count=200,
            comment_count=20,
            post_url="https://instiz.net/abc",
            created_at=now,
            updated_at=now
        )
        session.add(post)
        session.flush()

        # 7. Instiz Comment
        instiz_comment = InstizComments(
            post_id=post.id,
            text="진짜 웃기다ㅋㅋ",
            created_at=now
        )
        session.add(instiz_comment)

        session.add(CollectedInstizPosts(
            post_id=post.id,
            keyword_id=keyword.id,
            collected_at=now
        ))
        session.add(CollectedInstizComments(
            comment_id=instiz_comment.id,
            keyword_id=keyword.id,
            collected_at=now
        ))

        # 8. Tiktok Video
        tiktok_video = TiktokVideos(
            id="ttv123",
            keyword_id=keyword.id,
            title="딸기라떼 만들기",
            video_url="https://tiktok.com/v/ttv123"
        )
        session.add(tiktok_video)

        session.add(CollectedTiktokVideos(
            video_id=tiktok_video.id,
            keyword_id=keyword.id,
            collected_at=now
        ))

        # 9. Tiktok Comment
        tiktok_comment = TiktokComments(
            id="ttc123",
            video_id=tiktok_video.id,
            text="먹고 싶다...",
            reply_count=2,
            user_id="u123",
            nickname="맛집러",
            parent_comment_id=None,
            is_reply=False,
            created_at=now
        )
        session.add(tiktok_comment)

        session.add(CollectedTiktokComments(
            comment_id=tiktok_comment.id,
            keyword_id=keyword.id,
            collected_at=now
        ))

        # 10. Sentiments / Aspects
        pos = Sentiments(label="positive", polarity=1)
        neg = Sentiments(label="negative", polarity=2)
        aspect = Aspects(name="맛")

        session.add_all([pos, neg, aspect])
        session.flush()

        # 11. AnalysisLogs + ContentAnalysis
        log = AnalysisLogs(started_at=now - timedelta(minutes=5), finished_at=now)
        session.add(log)
        session.flush()

        session.add(ContentAnalysis(
            analysis_log_id=log.id,
            source_type="youtube_comment",
            source_id=comment.id,
            sentence="정말 맛있어 보여요!",
            aspect_id=aspect.id,
            sentiment_id=pos.id,
            evidence_keywords="맛있어, 보여요"
        ))

        session.commit()
        print("✅ Dummy data inserted successfully!")

    except Exception as e:
        session.rollback()
        print("❌ Error inserting dummy data:", e)

    finally:
        session.close()

if __name__ == "__main__":
    insert_dummy_data()
