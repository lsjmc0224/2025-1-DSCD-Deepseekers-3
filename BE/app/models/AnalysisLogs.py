from sqlalchemy import Column, Integer, TIMESTAMP
from app.core.db import Base

class AnalysisLogs(Base):
    __tablename__ = "analysis_logs"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="Primary Key")
    started_at = Column(TIMESTAMP, comment="분석 시작 시각")
    finished_at = Column(TIMESTAMP, comment="분석 종료 시각") 