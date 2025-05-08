from sqlalchemy import Column, Text, Integer, TIMESTAMP, ForeignKey, Index
from app.core.db import Base

class CollectedYoutubeComments(Base):
    __tablename__ = "collected_youtube_comments"
    comment_id = Column(Text, ForeignKey("youtube_comments.id"), primary_key=True, comment="YoutubeComments의 comment ID")
    keyword_id = Column(Integer, ForeignKey("keywords.id"), primary_key=True, comment="Keywords의 키워드 ID")
    collected_at = Column(TIMESTAMP, comment="댓글 수집 시각")

    __table_args__ = (
        Index("idx_collected_youtube_comments_collected_at", "collected_at"),
    ) 