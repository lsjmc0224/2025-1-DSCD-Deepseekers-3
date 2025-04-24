"""
데이터 수집 관련 스키마

데이터 수집 API에 사용되는 요청 및 응답 스키마를 정의합니다.
이 모듈은 YouTube 데이터 수집 요청 및 응답, 작업 상태 조회 등의 스키마를 포함합니다.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class YouTubeCollectionRequest(BaseModel):
    """
    YouTube 데이터 수집 요청 스키마
    
    수집할 YouTube 동영상 ID 목록 또는 검색 키워드를 지정하여 데이터 수집을 요청합니다.
    video_ids와 keywords 중 적어도 하나는 제공되어야 합니다.
    """
    video_ids: Optional[List[str]] = Field(
        None, 
        description="수집할 YouTube 동영상 ID 목록",
        json_schema_extra={"examples": ["dQw4w9WgXcQ", "9bZkp7q19f0"]}
    )
    keywords: Optional[List[str]] = Field(
        None, 
        description="검색할 키워드 목록 - 이 키워드들로 YouTube에서 동영상을 검색합니다",
        json_schema_extra={"examples": ["편의점 디저트 리뷰", "신상 과자 추천"]}
    )
    max_comments: int = Field(
        100, 
        description="각 비디오당 최대 수집 댓글 수 (1-1000)",
        ge=1,
        le=1000,
        json_schema_extra={"examples": [200]}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "video_ids": ["dQw4w9WgXcQ", "9bZkp7q19f0"],
                "keywords": ["편의점 디저트 리뷰", "신상 과자 추천"],
                "max_comments": 200
            }]
        }
    )


class YouTubeCollectionResponse(BaseModel):
    """
    YouTube 데이터 수집 응답 스키마
    
    데이터 수집 요청이 성공적으로 처리되었을 때 반환되는 응답입니다.
    요청 ID를 통해 수집 작업의 상태를 추적할 수 있습니다.
    """
    status: str = Field(
        ..., 
        description="요청 처리 상태 (success 또는 error)",
        json_schema_extra={"examples": ["success"]}
    )
    message: str = Field(
        ..., 
        description="상태 메시지",
        json_schema_extra={"examples": ["YouTube 데이터 수집 작업이 시작되었습니다."]}
    )
    request_id: str = Field(
        ..., 
        description="추적에 사용할 수 있는 요청 ID",
        json_schema_extra={"examples": ["youtube-a1b2c3d4e5f6"]}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "status": "success",
                "message": "YouTube 데이터 수집 작업이 시작되었습니다.",
                "request_id": "youtube-a1b2c3d4e5f6"
            }]
        }
    )


class CollectionStatusResponse(BaseModel):
    """
    데이터 수집 상태 응답 스키마
    
    데이터 수집 작업의 현재 상태를 나타냅니다.
    작업이 완료된 경우 collected_at 및 result 필드에 값이 채워집니다.
    """
    status: str = Field(
        ..., 
        description="작업 상태 (initialized, running, completed, failed)",
        json_schema_extra={"examples": ["running"]}
    )
    progress: float = Field(
        ..., 
        description="작업 진행률 (0.0-100.0)",
        ge=0.0,
        le=100.0,
        json_schema_extra={"examples": [65.5]}
    )
    message: str = Field(
        ..., 
        description="상태 메시지",
        json_schema_extra={"examples": ["2개의 동영상 중 1개 처리 완료, 댓글 수집 중..."]}
    )
    completed_at: Optional[datetime] = Field(
        None, 
        description="작업 완료 시간 (작업이 완료된 경우에만 값이 존재)",
        json_schema_extra={"examples": ["2023-07-28T15:30:45Z"]}
    )
    result: Optional[Dict[str, Any]] = Field(
        None, 
        description="작업 결과 데이터 (작업이 완료된 경우에만 값이 존재)",
        json_schema_extra={"examples": [{
            "videos_collected": 2,
            "comments_collected": 350,
            "error_count": 0,
            "video_ids": ["dQw4w9WgXcQ", "9bZkp7q19f0"]
        }]}
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{
                "status": "completed",
                "progress": 100.0,
                "message": "데이터 수집 완료",
                "completed_at": "2023-07-28T15:30:45Z",
                "result": {
                    "videos_collected": 2,
                    "comments_collected": 350,
                    "error_count": 0,
                    "video_ids": ["dQw4w9WgXcQ", "9bZkp7q19f0"]
                }
            }]
        }
    ) 