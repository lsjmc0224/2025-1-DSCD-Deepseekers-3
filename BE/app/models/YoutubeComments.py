from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey, Integer, Index
from app.core.db import Base

class YoutubeComments(Base):
    __tablename__ = "youtube_comments"
    id = Column(Text, primary_key=True, comment="API에서 가져온 comment ID")
    video_id = Column(Text, ForeignKey("youtube_videos.id"), comment="비디오 ID")
    keyword_id = Column(Integer, ForeignKey("keywords.id"), comment="키워드 ID")
    text = Column(Text, comment="댓글 내용")
    created_at = Column(TIMESTAMP, comment="생성 시각")
    collected_at = Column(TIMESTAMP, comment="수집 시각")

    __table_args__ = (
        Index("idx_youtube_comments_created_at", "created_at"),
        Index("idx_youtube_comments_collected_at", "collected_at"),
    ) 