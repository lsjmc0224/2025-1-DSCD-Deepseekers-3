from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, Index
from app.core.db import Base

class InstizComments(Base):
    __tablename__ = "instiz_comments"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="Primary Key")
    post_id = Column(Integer, ForeignKey("instiz_posts.id"), comment="게시글 ID")
    keyword_id = Column(Integer, ForeignKey("keywords.id"), comment="키워드 ID")
    text = Column(Text, comment="댓글 내용")
    created_at = Column(TIMESTAMP, comment="생성 시각")
    collected_at = Column(TIMESTAMP, comment="수집 시각")

    __table_args__ = (
        Index("idx_instiz_comments_created_at", "created_at"),
        Index("idx_instiz_comments_collected_at", "collected_at"),
    ) 