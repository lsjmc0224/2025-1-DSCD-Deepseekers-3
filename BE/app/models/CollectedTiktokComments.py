from sqlalchemy import Column, Text, Integer, TIMESTAMP, ForeignKey, Index
from app.core.db import Base

class CollectedTiktokComments(Base):
    __tablename__ = "collected_tiktok_comments"
    comment_id = Column(Text, ForeignKey("tiktok_comments.id"), primary_key=True, comment="댓글 ID")
    keyword_id = Column(Integer, ForeignKey("keywords.id"), primary_key=True, comment="키워드 ID")
    collected_at = Column(TIMESTAMP, comment="수집 시각")

    __table_args__ = (
        Index("idx_collected_tiktok_comments_collected_at", "collected_at"),
    ) 