"""
데이터 수집 API 엔드포인트

YouTube 동영상 및 댓글을 수집하기 위한 엔드포인트를 제공합니다.
데이터 수집 작업을 비동기적으로 처리하고 작업 상태를 조회할 수 있습니다.
"""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas import data_collection as schemas
from app.services.collectors import collect_youtube_data, generate_request_id, get_collection_status

router = APIRouter()


@router.post(
    "/youtube", 
    response_model=schemas.YouTubeCollectionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="YouTube 데이터 수집 요청",
    description="YouTube에서 동영상 정보, 댓글, 메타데이터를 수집하는 비동기 작업을 시작합니다."
)
async def collect_youtube_data_endpoint(
    request: schemas.YouTubeCollectionRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    YouTube에서 데이터 수집 작업을 시작합니다.
    
    비디오 ID 목록이나 검색 키워드를 통해 YouTube에서 데이터를 수집합니다.
    작업은 비동기적으로 처리되며, 요청 ID를 통해 상태를 조회할 수 있습니다.
    
    - **video_ids**: 직접 수집할 YouTube 동영상 ID 목록
    - **keywords**: 검색할 키워드 목록 (video_ids가 없을 경우 사용)
    - **max_comments**: 각 동영상마다 수집할 최대 댓글 수
    
    Returns:
        요청 상태와 추적을 위한 요청 ID를 포함한 응답
        
    Examples:
        ```json
        {
          "status": "success",
          "message": "YouTube 데이터 수집 작업이 시작되었습니다.",
          "request_id": "youtube-a1b2c3d4e5f6"
        }
        ```
    """
    # 비디오 ID 또는 키워드 중 하나는 반드시 제공되어야 함
    if not request.video_ids and not request.keywords:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="video_ids 또는 keywords 중 하나는 반드시 제공해야 합니다."
        )
    
    # 백그라운드 작업으로 데이터 수집 요청 등록
    request_id = "youtube-" + generate_request_id()
    background_tasks.add_task(
        collect_youtube_data,
        video_ids=request.video_ids,
        keywords=request.keywords,
        max_comments=request.max_comments,
        request_id=request_id.replace("youtube-", ""),
        db=db
    )
    
    return {
        "status": "success",
        "message": "YouTube 데이터 수집 작업이 시작되었습니다.",
        "request_id": request_id
    }


@router.get(
    "/status/{request_id}", 
    response_model=schemas.CollectionStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="데이터 수집 상태 조회", 
    description="요청 ID를 사용하여 데이터 수집 작업의 현재 상태를 조회합니다.",
    responses={
        404: {
            "description": "요청 ID를 찾을 수 없음",
            "content": {
                "application/json": {
                    "example": {"detail": "요청 ID를 찾을 수 없습니다."}
                }
            }
        }
    }
)
async def get_collection_status_endpoint(
    request_id: str,
    db: AsyncSession = Depends(get_db),
) -> Any:
    """
    데이터 수집 작업의 상태를 조회합니다.
    
    요청 ID를 사용하여 이전에 요청한 데이터 수집 작업의 상태를 확인합니다.
    작업 상태, 진행률, 결과 등을 반환합니다.
    
    Args:
        request_id: 데이터 수집 요청 시 받은 요청 ID
        
    Returns:
        작업 상태, 진행률, 메시지, 완료 시간, 결과를 포함한 응답
        
    Raises:
        HTTPException: 요청 ID가 유효하지 않거나 찾을 수 없는 경우
        
    Examples:
        ```json
        {
          "status": "running",
          "progress": 65.5,
          "message": "2개의 동영상 중 1개 처리 완료, 댓글 수집 중...",
          "completed_at": null,
          "result": null
        }
        ```
    """
    # 요청 ID로 작업 상태 조회
    if request_id.startswith("youtube-"):
        status = await get_collection_status(request_id.replace("youtube-", ""), db)
        
        return {
            "status": status["status"],
            "progress": status["progress"],
            "message": status["message"],
            "completed_at": status["completed_at"],
            "result": status["result"]
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="요청 ID를 찾을 수 없습니다."
        ) 