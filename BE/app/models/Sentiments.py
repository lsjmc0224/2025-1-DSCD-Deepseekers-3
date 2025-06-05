from sqlalchemy import Column, Integer, Text, UniqueConstraint
from app.core.db import Base

class Sentiments(Base):
    __tablename__ = "sentiments"
    id = Column(Integer, primary_key=True, autoincrement=False, comment="감정 ID (0: 부정, 1: 긍정)")
    label = Column(Text, unique=True, nullable=False, comment="감정 레이블")