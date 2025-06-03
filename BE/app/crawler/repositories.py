from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Dict

from app.models import InstizPosts, CollectedInstizPosts


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
                    keyword_id=keyword_id,  # 원본 기록용
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
