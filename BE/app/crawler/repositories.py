from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Dict, Optional
from collections import defaultdict
from datetime import datetime

from app.models import (
    InstizPosts, CollectedInstizPosts, TiktokVideos, 
    TiktokComments, CollectedTiktokComments, CollectedTiktokVideos, 
    YoutubeChannels, YoutubeVideos, CollectedYoutubeVideos,
    YoutubeComments, CollectedYoutubeComments
)


class CrawlingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_instiz_posts(self, posts: List[Dict]):
        """
        Instiz 크롤러 결과를 InstizPosts 및 CollectedInstizPosts 테이블에 저장합니다.
        - 동일한 게시글이 여러 키워드로 수집될 수 있으므로,
          InstizPosts(post_url 기준 중복 제거)와 CollectedInstizPosts(post_id + keyword_id 중복 제거)를 함께 저장합니다.
        """
        saved_posts = 0
        saved_collections = 0

        for post in posts:
            keyword_id = post["keyword_id"]
            post_url = post["post_url"]
            collected_at = post["collected_at"]

            # 1. 이미 동일한 post_url이 InstizPosts에 있는지 확인
            existing_post = self.db.query(InstizPosts).filter_by(post_url=post_url).first()

            if existing_post:
                post_id = existing_post.id
            else:
                # 새로운 게시글이면 InstizPosts에 저장
                new_post = InstizPosts(
                    content=post["content"],
                    view_count=post["view_count"],
                    like_count=post["like_count"],
                    comment_count=post["comment_count"],
                    post_url=post_url,
                    created_at=post["created_at"],
                    updated_at=post["updated_at"],
                    collected_at=collected_at,
                    is_analyzed=False
                )
                self.db.add(new_post)
                self.db.flush()  # post_id 확보를 위해 flush
                post_id = new_post.id
                saved_posts += 1

            # 2. CollectedInstizPosts 중복 확인
            already_collected = self.db.query(CollectedInstizPosts).filter_by(
                post_id=post_id, keyword_id=keyword_id
            ).first()

            if not already_collected:
                collected = CollectedInstizPosts(
                    post_id=post_id,
                    keyword_id=keyword_id,
                    collected_at=collected_at
                )
                self.db.add(collected)
                saved_collections += 1

        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            print(f"[ERROR] DB 저장 중 오류 발생: {e}")

        return {"posts_saved": saved_posts, "collections_saved": saved_collections}
    
    def create_tiktok_videos(self, videos: List[Dict]) -> Dict[str, int]:
        saved_videos = 0
        saved_collections = 0

        for video in videos:
            video_id = video["id"]
            keyword_id = video["keyword_id"]
            collected_at = video["collected_at"]

            # 중복 확인
            existing_video = self.db.query(TiktokVideos).filter_by(id=video_id).first()

            if not existing_video:
                new_video = TiktokVideos(
                    id=video_id,
                    title=video["title"],
                    video_url=video["video_url"],
                    collected_at=collected_at,
                )
                self.db.add(new_video)
                self.db.flush()  # id 이미 명시되어 있어도 flush는 일관성 위해 호출
                saved_videos += 1

            # CollectedTiktokVideos 중복 확인
            already_collected = self.db.query(CollectedTiktokVideos).filter_by(
                comment_id=video_id, keyword_id=keyword_id
            ).first()

            if not already_collected:
                self.db.add(CollectedTiktokVideos(
                    comment_id=video_id,
                    keyword_id=keyword_id,
                    collected_at=collected_at
                ))
                saved_collections += 1

        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            print(f"[ERROR] TikTok Video 저장 중 오류 발생: {e}")

        return {"videos_saved": saved_videos, "video_collections_saved": saved_collections}

    def create_tiktok_comments(self, comments: List[Dict]) -> Dict[str, int]:
        saved_comments = 0
        saved_collections = 0

        unique_map = {}
        for comment in comments:
            key = (comment["id"], comment["keyword_id"])
            if key not in unique_map:
                unique_map[key] = comment  # 덮어써도 무방

        # ✅ 1단계: 댓글 먼저 저장
        for (comment_id, _), comment in unique_map.items():
            existing_comment = self.db.query(TiktokComments).filter_by(id=comment_id).first()
            if not existing_comment:
                new_comment = TiktokComments(
                    id=comment_id,
                    video_id=comment["video_id"],
                    content=comment["content"],
                    reply_count=comment["reply_count"],
                    user_id=comment["user_id"],
                    nickname=comment["nickname"],
                    parent_comment_id=comment["parent_comment_id"],
                    is_reply=comment["is_reply"],
                    created_at=comment["created_at"],
                    is_analyzed=False
                )
                self.db.add(new_comment)
                saved_comments += 1

        # ✅ flush() 호출: 댓글 먼저 DB에 반영 (ID 존재 보장)
        self.db.flush()

        # ✅ 2단계: CollectedTiktokComments 저장
        for (comment_id, keyword_id), comment in unique_map.items():
            collected_at = comment["collected_at"]
            already_collected = self.db.query(CollectedTiktokComments).filter_by(
                comment_id=comment_id,
                keyword_id=keyword_id
            ).first()

            if not already_collected:
                self.db.add(CollectedTiktokComments(
                    comment_id=comment_id,
                    keyword_id=keyword_id,
                    collected_at=collected_at
                ))
                saved_collections += 1

        try:
            self.db.commit()
        except IntegrityError as e:
            self.db.rollback()
            print(f"[ERROR] TikTok Comment 저장 중 오류 발생: {e}")

        return {
            "comments_saved": saved_comments,
            "comment_collections_saved": saved_collections
        }

    def create_youtube_data(
        self,
        channels: List[Dict],
        videos: List[Dict],
        comments: List[Dict]
    ) -> Optional[Dict[str, int]]:
        saved_channels = 0
        saved_videos = 0
        saved_collected_videos = 0
        saved_comments = 0
        saved_collected_comments = 0

        try:
            # 1. 채널 저장
            for ch in channels:
                if not ch or not ch["id"]:
                    continue
                existing_channel = self.db.query(YoutubeChannels).filter_by(id=ch["id"]).first()
                if not existing_channel:
                    new_channel = YoutubeChannels(
                        id=ch["id"],
                        name=ch["name"],
                        subscriber_count=ch["subscriber_count"],
                        updated_at=ch["updated_at"]
                    )
                    self.db.add(new_channel)
                    saved_channels += 1

            # 2. 영상 저장 + 수집 이력
            for v in videos:
                video_id = v["id"]
                keyword_id = v["keyword_id"]
                collected_at = v["collected_at"]

                existing_video = self.db.query(YoutubeVideos).filter_by(id=video_id).first()
                if not existing_video:
                    new_video = YoutubeVideos(
                        id=video_id,
                        channel_id=v["channel_id"],
                        created_at=v["created_at"],
                        collected_at=collected_at,
                        like_count=v["like_count"],
                        comment_count=v["comment_count"],
                        view_count=v["view_count"],
                        updated_at=v["updated_at"],
                        video_type=v["video_type"],
                        title=v.get("title", ""),
                        thumbnail_url=v.get("thumbnail_url", "")
                    )
                    self.db.add(new_video)
                    self.db.flush()
                    saved_videos += 1

                already_collected_video = self.db.query(CollectedYoutubeVideos).filter_by(
                    video_id=video_id,
                    keyword_id=keyword_id
                ).first()
                if not already_collected_video:
                    self.db.add(CollectedYoutubeVideos(
                        video_id=video_id,
                        keyword_id=keyword_id,
                        collected_at=collected_at
                    ))
                    saved_collected_videos += 1

            self.db.flush()

            # 3. 댓글 저장 + 수집 이력
            for c in comments:
                comment_id = c["id"]
                video_id = c["video_id"]
                keyword_id = c["keyword_id"]
                created_at = c["created_at"]
                like_count = c["like_count"]

                existing_comment = self.db.query(YoutubeComments).filter_by(id=comment_id).first()
                if not existing_comment:
                    new_comment = YoutubeComments(
                        id=comment_id,
                        video_id=video_id,
                        content=c["content"],
                        created_at=created_at,
                        is_analyzed=False,
                        like_count=like_count
                    )
                    self.db.add(new_comment)
                    self.db.flush()
                    saved_comments += 1

                already_collected_comment = self.db.query(CollectedYoutubeComments).filter_by(
                    comment_id=comment_id,
                    keyword_id=keyword_id
                ).first()
                if not already_collected_comment:
                    self.db.add(CollectedYoutubeComments(
                        comment_id=comment_id,
                        keyword_id=keyword_id,
                        collected_at=c.get("collected_at", datetime.now())
                    ))
                    saved_collected_comments += 1

            self.db.commit()

            return {
                "channels_saved": saved_channels,
                "videos_saved": saved_videos,
                "collected_videos_saved": saved_collected_videos,
                "comments_saved": saved_comments,
                "collected_comments_saved": saved_collected_comments
            }

        except IntegrityError as e:
            self.db.rollback()
            print(f"[ERROR] YouTube 데이터 저장 중 오류 발생: {e}")
            return None
