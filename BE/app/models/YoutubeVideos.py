from sqlalchemy import Column, Text, Integer, TIMESTAMP, ForeignKey, Index
from app.core.db import Base

class YoutubeVideos(Base):
    __tablename__ = "youtube_videos"
    id = Column(Text, primary_key=True, comment="API에서 가져온 video ID")
    keyword_id = Column(Integer, ForeignKey("keywords.id"), comment="키워드 ID")
    channel_id = Column(Text, ForeignKey("youtube_channels.id"), comment="채널 ID")
    created_at = Column(TIMESTAMP, comment="생성 시각")
    collected_at = Column(TIMESTAMP, comment="수집 시각")
    like_count = Column(Integer, comment="좋아요 수")
    comment_count = Column(Integer, comment="댓글 수")
    view_count = Column(Integer, comment="조회수")
    updated_at = Column(TIMESTAMP, comment="업데이트 시각")

    __table_args__ = (
        Index("idx_youtube_videos_created_at", "created_at"),
        Index("idx_youtube_videos_collected_at", "collected_at"),
    )