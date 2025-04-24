from fastapi import APIRouter

from app.api.endpoints import data_collection, analysis, dashboard, notifications, admin, health

api_router = APIRouter()

# 데이터 수집 관련 엔드포인트
api_router.include_router(
    data_collection.router,
    prefix="/data-collection",
    tags=["data-collection"]
)

# 데이터 분석 관련 엔드포인트
api_router.include_router(
    analysis.router,
    prefix="/analysis",
    tags=["analysis"]
)

# 대시보드 관련 엔드포인트
api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["dashboard"]
)

# 알림 관련 엔드포인트
api_router.include_router(
    notifications.router,
    prefix="/notifications",
    tags=["notifications"]
)

# 관리자 관련 엔드포인트
api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"]
)

api_router.include_router(health.router, prefix="/health", tags=["health"]) 