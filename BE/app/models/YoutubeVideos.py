from sqlalchemy import Column, Text, Integer, TIMESTAMP, ForeignKey, Index
from app.core.db import Base

class YoutubeVideos(Base):
    __tablename__ = "youtube_videos"
    id = Column(Text, primary_key=True, comment="API에서 가져온 video ID")
    channel_id = Column(Text, ForeignKey("youtube_channels.id"), comment="채널 ID")
    created_at = Column(TIMESTAMP, comment="영상 업로드 시각")
    collected_at = Column(TIMESTAMP, comment="영상 수집 시각")
    like_count = Column(Integer, comment="좋아요 수")
    comment_count = Column(Integer, comment="댓글 수")
    view_count = Column(Integer, comment="조회수")
    updated_at = Column(TIMESTAMP, comment="영상 정보 갱신 시각")
    video_type = Column(Text, comment="숏폼(short), 롱폼(long) 영상 타입 정보")

    __table_args__ = (
        Index("idx_youtube_videos_created_at", "created_at"),
        Index("idx_youtube_videos_collected_at", "collected_at"),
    )