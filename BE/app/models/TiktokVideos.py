from sqlalchemy import Column, Text, TIMESTAMP, Index, ForeignKey, Integer
from app.core.db import Base

class TiktokVideos(Base):
    __tablename__ = "tiktok_videos"
    id = Column(Text, primary_key=True, comment="video ID from API")
    keyword_id = Column(Integer, ForeignKey("keywords.id"), comment="키워드 ID")
    title = Column(Text, comment="제목")
    video_url = Column(Text, comment="비디오 URL")
    collected_at = Column(TIMESTAMP, comment="수집 시각")

    __table_args__ = (
        Index("idx_tiktok_videos_collected_at", "collected_at"),
    ) 