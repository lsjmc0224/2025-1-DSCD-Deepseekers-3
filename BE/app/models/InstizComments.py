from sqlalchemy import Column, Integer, Text, TIMESTAMP, ForeignKey, Index
from app.core.db import Base

class InstizComments(Base):
    __tablename__ = "instiz_comments"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="댓글 고유 ID")
    post_id = Column(Integer, ForeignKey("instiz_posts.id"), comment="게시글 ID")
    text = Column(Text, comment="댓글 내용")
    created_at = Column(TIMESTAMP, comment="댓글 작성 시각")

    __table_args__ = (
        Index("idx_instiz_comments_created_at", "created_at"),
    ) 