from sqlalchemy import Column, Text, Integer, TIMESTAMP, ForeignKey, Index
from app.core.db import Base

class CollectedTiktokComments(Base):
    __tablename__ = "collected_tiktok_comments"
    comment_id = Column(Text, ForeignKey("tiktok_comments.id", ondelete="CASCADE"), primary_key=True, comment="TiktokComments의 댓글 ID")
    keyword_id = Column(Integer, ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True, comment="Keywords의 키워드 ID")
    collected_at = Column(TIMESTAMP, comment="댓글 수집 시각")

    __table_args__ = (
        Index("idx_collected_tiktok_comments_collected_at", "collected_at"),
    ) 