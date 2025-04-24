"""
알림 관련 API 엔드포인트

감성 분석 결과와 키워드 추출 결과에 대한 알림 설정 및 전송 기능을 제공합니다.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

# 라우터 정의
router = APIRouter()


# 모델 정의
class NotificationRule(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    type: str = Field(..., description="알림 유형 (sentiment, keyword)")
    conditions: Dict[str, Any] = Field(..., description="알림 조건")
    channels: List[str] = Field(..., description="알림 채널 (email, slack, webhook)")
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class NotificationHistory(BaseModel):
    id: Optional[int] = None
    rule_id: int
    message: str
    channels: List[str]
    sent_at: datetime
    status: str
    
    class Config:
        orm_mode = True


# API 엔드포인트
@router.get("/rules", response_model=List[NotificationRule])
async def get_notification_rules(
    type: Optional[str] = Query(None, description="알림 유형 (sentiment, keyword)"),
    db: AsyncSession = Depends(get_db)
):
    """
    알림 규칙 목록을 조회합니다.
    """
    # TODO: 실제 데이터베이스 연동 로직 구현
    return [
        {
            "id": 1,
            "name": "부정 감성 경고",
            "description": "부정 감성 비율이 30% 이상일 때 알림",
            "type": "sentiment",
            "conditions": {
                "sentiment": "negative",
                "threshold": 0.3,
                "period": "day"
            },
            "channels": ["email", "slack"],
            "is_active": True,
            "created_at": datetime.now()
        },
        {
            "id": 2,
            "name": "키워드 알림",
            "description": "특정 키워드 등장 시 알림",
            "type": "keyword",
            "conditions": {
                "keywords": ["품질", "이슈", "문제"],
                "count_threshold": 5,
                "period": "day"
            },
            "channels": ["slack"],
            "is_active": True,
            "created_at": datetime.now()
        }
    ]


@router.post("/rules", response_model=NotificationRule)
async def create_notification_rule(
    rule: NotificationRule = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """
    새로운 알림 규칙을 생성합니다.
    """
    # TODO: 실제 데이터베이스 연동 로직 구현
    rule_dict = rule.dict()
    rule_dict["id"] = 3  # 가상 ID 할당
    rule_dict["created_at"] = datetime.now()
    return rule_dict


@router.get("/history", response_model=List[NotificationHistory])
async def get_notification_history(
    start_date: Optional[datetime] = Query(None, description="시작 날짜"),
    end_date: Optional[datetime] = Query(None, description="종료 날짜"),
    rule_id: Optional[int] = Query(None, description="알림 규칙 ID"),
    limit: int = Query(20, description="결과 제한 수"),
    offset: int = Query(0, description="결과 오프셋"),
    db: AsyncSession = Depends(get_db)
):
    """
    알림 전송 이력을 조회합니다.
    """
    # TODO: 실제 데이터베이스 연동 로직 구현
    return [
        {
            "id": 1,
            "rule_id": 1,
            "message": "부정 감성 비율이 35%로 증가했습니다.",
            "channels": ["email", "slack"],
            "sent_at": datetime.now() - timedelta(days=1),
            "status": "success"
        },
        {
            "id": 2,
            "rule_id": 2,
            "message": "키워드 '품질 이슈'가 오늘 7회 언급되었습니다.",
            "channels": ["slack"],
            "sent_at": datetime.now() - timedelta(hours=6),
            "status": "success"
        }
    ] 