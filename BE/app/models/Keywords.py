from sqlalchemy import Column, Integer, Text
from app.core.db import Base

class Keywords(Base):
    __tablename__ = "keywords"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="Primary Key")
    keyword = Column(Text, comment="키워드") 