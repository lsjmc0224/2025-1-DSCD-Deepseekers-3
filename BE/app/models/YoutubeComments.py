from sqlalchemy import Column, Text, TIMESTAMP, ForeignKey, Index, Boolean
from app.core.db import Base

class YoutubeComments(Base):
    __tablename__ = "youtube_comments"
    id = Column(Text, primary_key=True, comment="API에서 가져온 comment ID")
    video_id = Column(Text, ForeignKey("youtube_videos.id"), comment="비디오 ID")
    content = Column(Text, comment="댓글 내용")
    created_at = Column(TIMESTAMP, comment="댓글 작성 시각")
    is_analyzed = Column(Boolean, default=False, comment="분석 여부")

    __table_args__ = (
        Index("idx_youtube_comments_created_at", "created_at"),
    ) 