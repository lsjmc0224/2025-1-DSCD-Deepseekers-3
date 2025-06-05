from sqlalchemy import Column, Text, Integer, TIMESTAMP, ForeignKey, Index
from app.core.db import Base

class TiktokVideos(Base):
    __tablename__ = "tiktok_videos"
    id = Column(Text, primary_key=True, comment="API에서 가져온 TikTok video ID")
    title = Column(Text, comment="영상 제목")
    video_url = Column(Text, comment="비디오 URL")
    collected_at = Column(TIMESTAMP, comment="영상 수집 시각")

    __table_args__ = (
        Index("idx_tiktok_videos_collected_at", "collected_at"),
    ) 