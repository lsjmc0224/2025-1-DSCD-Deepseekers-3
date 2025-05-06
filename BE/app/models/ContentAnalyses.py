from sqlalchemy import Column, Integer, Text, ForeignKey
from app.core.db import Base

class ContentAnalyses(Base):
    __tablename__ = "content_analyses"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="Primary Key")
    analysis_log_id = Column(Integer, ForeignKey("analysis_logs.id"), comment="분석 로그 ID")
    source_type = Column(Text, comment="소스 타입")
    source_id = Column(Text, comment="소스 ID")
    sentence = Column(Text, comment="문장")
    aspect_id = Column(Integer, ForeignKey("aspects.id"), comment="속성 ID")
    sentiment_id = Column(Integer, ForeignKey("sentiments.id"), comment="감정 ID")
    evidence_keywords = Column(Text, comment="근거 키워드") 