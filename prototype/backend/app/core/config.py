import secrets
import os
from typing import Any, Dict, List, Optional, Union

from pydantic import (
    AnyHttpUrl, 
    PostgresDsn, 
    Field,
    field_validator
)
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    애플리케이션 설정
    
    환경 변수를 통해 설정하며, 기본값을 제공합니다.
    """
    # 기본 설정
    SECRET_KEY: str = secrets.token_urlsafe(32)
    PROJECT_NAME: str = "YouTubeDataPortal"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # CORS 설정
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 데이터베이스 설정
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "app"
    POSTGRES_PORT: str = "5432"
    DATABASE_URI: Optional[str] = None

    @field_validator("DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        
        data = info.data
        user = data.get("POSTGRES_USER", "postgres")
        password = data.get("POSTGRES_PASSWORD", "postgres")
        host = data.get("POSTGRES_SERVER", "localhost")
        port = data.get("POSTGRES_PORT", "5432")
        db = data.get("POSTGRES_DB", "app")
        
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
    
    # Redis 설정
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_URI: Optional[str] = None
    
    @field_validator("REDIS_URI", mode="before")
    def assemble_redis_connection(cls, v: Optional[str], info) -> Any:
        if isinstance(v, str):
            return v
        
        data = info.data
        password = data.get("REDIS_PASSWORD")
        password_part = f":{password}@" if password else ""
        host = data.get("REDIS_HOST", "localhost")
        port = data.get("REDIS_PORT", "6379")
        db = data.get("REDIS_DB", 0)
        
        return f"redis://{password_part}{host}:{port}/{db}"
    
    # Prefect 설정
    PREFECT_API_URL: str = "http://localhost:4200/api"
    PREFECT_API_KEY: Optional[str] = None
    
    # YouTube API 설정
    YOUTUBE_API_KEY: str = ""
    
    # S3 스토리지 설정
    S3_ENDPOINT_URL: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None  
    S3_SECRET_KEY: Optional[str] = None
    S3_BUCKET_NAME: str = "youtube-data"
    
    # 파일 경로 설정
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    TEMP_DIR: str = os.path.join(DATA_DIR, "temp")
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 문서 URL 설정
    DOCS_URL: Optional[str] = "/docs"
    REDOC_URL: Optional[str] = "/redoc"
    OPENAPI_URL: Optional[str] = "/openapi.json"
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = os.path.join(BASE_DIR, "logs", "app.log")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore"
    }


settings = Settings() 