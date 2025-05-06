from sqlalchemy import Column, Integer, Text, UniqueConstraint
from app.core.db import Base

class Sentiments(Base):
    __tablename__ = "sentiments"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="Primary Key")
    label = Column(Text, unique=True, nullable=False, comment="감정 레이블")
    polarity = Column(Integer, comment="1: positive, 2: negative") 