# app/core/config.py

from pydantic_settings import BaseSettings
from pydantic import PostgresDsn
from typing import Optional
from dotenv import load_dotenv
from pathlib import Path

# 프로젝트 루트 기준으로 절대경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # app/core/config.py → app/core → app → BE (루트)
load_dotenv(dotenv_path=BASE_DIR / ".env")

class Settings(BaseSettings):
    # 기본 설정
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Analysis Backend"
    
    # 데이터베이스 설정
    DATABASE_URL: PostgresDsn  # 필수값, 타입 검증됨
    
    # JWT 설정
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days

    # YouTube API 키
    YOUTUBE_API_KEY: str  # .env에서 YOUTUBE_API_KEY로 불러옴

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
