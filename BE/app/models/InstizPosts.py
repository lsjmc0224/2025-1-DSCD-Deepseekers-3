from sqlalchemy import Column, Integer, Text, TIMESTAMP, Index, ForeignKey, Boolean
from app.core.db import Base

class InstizPosts(Base):
    __tablename__ = "instiz_posts"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="게시글 고유 ID")
    keyword_id = Column(Integer, ForeignKey("keywords.id"), comment="키워드 ID")
    content = Column(Text, comment="게시글 내용")
    view_count = Column(Integer, comment="조회수")
    like_count = Column(Integer, comment="좋아요 수")
    comment_count = Column(Integer, comment="댓글 수")
    post_url = Column(Text, comment="게시글 URL")
    created_at = Column(TIMESTAMP, comment="게시글 작성 시각")
    updated_at = Column(TIMESTAMP, comment="게시글 정보 갱신 시각")
    collected_at = Column(TIMESTAMP, comment="수집 시각")
    is_analyzed = Column(Boolean, default=False, comment="분석 여부")

    __table_args__ = (
        Index("idx_instiz_posts_created_at", "created_at"),
        Index("idx_instiz_posts_collected_at", "collected_at"),
    ) 