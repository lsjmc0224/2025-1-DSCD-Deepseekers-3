from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, Index
from app.core.db import Base

class CollectedInstizPosts(Base):
    __tablename__ = "collected_instiz_posts"
    post_id = Column(Integer, ForeignKey("instiz_posts.id"), primary_key=True, comment="InstizPosts의 게시글 ID")
    keyword_id = Column(Integer, ForeignKey("keywords.id"), primary_key=True, comment="Keywords의 키워드 ID")
    collected_at = Column(TIMESTAMP, comment="게시글 수집 시각")

    __table_args__ = (
        Index("idx_collected_instiz_posts_collected_at", "collected_at"),
    ) 