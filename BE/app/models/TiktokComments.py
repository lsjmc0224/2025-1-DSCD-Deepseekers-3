from sqlalchemy import Column, Text, Integer, Boolean, TIMESTAMP, ForeignKey, Index
from app.core.db import Base

class TiktokComments(Base):
    __tablename__ = "tiktok_comments"
    id = Column(Text, primary_key=True, comment="댓글 ID")
    video_id = Column(Text, ForeignKey("tiktok_videos.id"), comment="비디오 ID")
    text = Column(Text, comment="댓글 내용")
    reply_count = Column(Integer, comment="답글 수")
    user_id = Column(Text, comment="유저 ID")
    nickname = Column(Text, comment="닉네임")
    parent_comment_id = Column(Text, ForeignKey("tiktok_comments.id"), comment="부모 댓글 ID")
    is_reply = Column(Boolean, comment="답글 여부")
    created_at = Column(TIMESTAMP, comment="댓글 작성 시각")

    __table_args__ = (
        Index("idx_tiktok_comments_created_at", "created_at"),
    ) 