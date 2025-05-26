from sqlalchemy import Column, Text, Integer, TIMESTAMP, ForeignKey, Index
from app.core.db import Base

class CollectedYoutubeVideos(Base):
    __tablename__ = "collected_youtube_videos"
    video_id = Column(Text, ForeignKey("youtube_videos.id"), primary_key=True, comment="YoutubeVideo의 ID")
    keyword_id = Column(Integer, ForeignKey("keywords.id"), primary_key=True, comment="Keywords의 키워드 ID")
    collected_at = Column(TIMESTAMP, comment="댓글 수집 시각")

    __table_args__ = (
        Index("idx_collected_youtube_videos_collected_at", "collected_at"),
    ) 