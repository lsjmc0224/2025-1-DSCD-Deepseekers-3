from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# class UserBase(BaseModel):
#     email: EmailStr
#     username: str

# class UserCreate(UserBase):
#     password: str

# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str

# class UserResponse(UserBase):
#     id: str
#     created_at: datetime
#     is_active: bool

# class Token(BaseModel):
#     access_token: str
#     token_type: str 