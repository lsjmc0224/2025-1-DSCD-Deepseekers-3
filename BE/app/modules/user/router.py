from fastapi import APIRouter, Depends
from . import schemas

# router = APIRouter()

# @router.post("/create", response_model=schemas.UserResponse)
# async def create_user(user: schemas.UserCreate):
#     # TODO: Implement user creation
#     pass

# @router.post("/login", response_model=schemas.Token)
# async def login(user: schemas.UserLogin):
#     # TODO: Implement user login
#     pass

# 유저 로그아웃은 프론트엔드 변수 초기화로 달성하기
# @router.post("/logout")
# async def logout():
#     # TODO: Implement user logout
#     pass

# @router.post("/delete")
# async def delete_user():
#     # TODO: Implement user deletion
#     pass 