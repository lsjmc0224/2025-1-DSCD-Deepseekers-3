from sqlalchemy import Column, Integer, Text
from app.core.db import Base

class Aspects(Base):
    __tablename__ = "aspects"
    id = Column(Integer, primary_key=True, autoincrement=True, comment="Primary Key")
    name = Column(Text, comment="속성명") 