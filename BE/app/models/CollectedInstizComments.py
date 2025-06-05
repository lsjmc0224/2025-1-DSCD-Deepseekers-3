from sqlalchemy import Column, Integer, TIMESTAMP, ForeignKey, Index
from app.core.db import Base

class CollectedInstizComments(Base):
    __tablename__ = "collected_instiz_comments"
    comment_id = Column(Integer, ForeignKey("instiz_comments.id", ondelete="CASCADE"), primary_key=True, comment="InstizComments의 댓글 ID")
    keyword_id = Column(Integer, ForeignKey("keywords.id", ondelete="CASCADE"), primary_key=True, comment="Keywords의 키워드 ID")
    collected_at = Column(TIMESTAMP, comment="댓글 수집 시각")

    __table_args__ = (
        Index("idx_collected_instiz_comments_collected_at", "collected_at"),
    ) 