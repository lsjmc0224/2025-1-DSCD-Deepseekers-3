from sqlalchemy import Column, Integer, Text, TIMESTAMP, Index, ForeignKey
from app.core.db import Base

class InstizPosts(Base):
    __tablename__ = "instiz_posts"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="Primary Key")
    keyword_id = Column(Integer, ForeignKey("keywords.id"), comment="키워드 ID")
    content = Column(Text, comment="게시글 내용")
    view_count = Column(Integer, comment="조회수")
    like_count = Column(Integer, comment="좋아요 수")
    comment_count = Column(Integer, comment="댓글 수")
    post_url = Column(Text, comment="게시글 URL")
    created_at = Column(TIMESTAMP, comment="생성 시각")
    updated_at = Column(TIMESTAMP, comment="업데이트 시각")
    collected_at = Column(TIMESTAMP, comment="수집 시각")

    __table_args__ = (
        Index("idx_instiz_posts_created_at", "created_at"),
        Index("idx_instiz_posts_collected_at", "collected_at"),
    ) 