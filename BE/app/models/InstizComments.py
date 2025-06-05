from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, Index, Boolean
from app.core.db import Base

class InstizComments(Base):
    __tablename__ = "instiz_comments"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="댓글 고유 ID")
    post_id = Column(Integer, ForeignKey("instiz_posts.id", ondelete="CASCADE"), comment="게시글 ID")
    content = Column(Text, comment="댓글 내용")
    created_at = Column(TIMESTAMP, comment="댓글 작성 시각")
    is_analyzed = Column(Boolean, default=False, comment="분석 여부")

    __table_args__ = (
        Index("idx_instiz_comments_created_at", "created_at"),
    ) 