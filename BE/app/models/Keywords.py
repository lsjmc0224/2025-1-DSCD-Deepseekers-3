from sqlalchemy import Column, Integer, Text, TIMESTAMP
from app.core.db import Base

class Keywords(Base):
    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="키워드 고유 ID")
    keyword = Column(Text, comment="검색 키워드")
    searched_at = Column(TIMESTAMP, comment="키워드가 검색된 시각")