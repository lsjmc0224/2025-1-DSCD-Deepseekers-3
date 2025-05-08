# app/models/Users.py

from sqlalchemy import Column, String
from app.core.db import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)  # UUID or email as PK도 가능
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
