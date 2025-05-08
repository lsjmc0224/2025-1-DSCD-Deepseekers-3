from sqlalchemy import Column, Text, TIMESTAMP, Index
from app.core.db import Base

class TiktokVideos(Base):
    __tablename__ = "tiktok_videos"
    id = Column(Text, primary_key=True, comment="video ID from API")
    title = Column(Text, comment="제목")
    video_url = Column(Text, comment="비디오 URL")
    # created_at = Column(TIMESTAMP, comment="생성 시각")
    # updated_at = Column(TIMESTAMP, comment="업데이트 시각")

    __table_args__ = (
        Index("idx_tiktok_videos_created_at", "created_at"),
    ) 