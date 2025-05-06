from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 기본 설정
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Analysis Backend"
    
    # 데이터베이스 설정
    DATABASE_URL: Optional[str] = None
    
    # JWT 설정
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings() 