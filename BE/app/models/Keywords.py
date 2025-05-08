from sqlalchemy import Column, Integer, Text, TIMESTAMP
from app.core.db import Base

class Keywords(Base):
    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="Primary Key")
    keyword = Column(Text, comment="키워드") 
    searched_at = Column(TIMESTAMP, comment="생성 시각")