from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.staticfiles import StaticFiles
import os
from contextlib import asynccontextmanager

from app.api.api import api_router
from app.core.config import settings

# API 태그 메타데이터 설정
tags_metadata = [
    {
        "name": "dashboard",
        "description": "대시보드에 필요한 데이터를 제공하는 엔드포인트입니다. 수집된 비디오, 댓글, 감성 분석 결과 등을 조회할 수 있습니다.",
    },
    {
        "name": "data-collection",
        "description": "YouTube에서 동영상 및 댓글 데이터를 수집하는 엔드포인트입니다. 데이터 수집 작업을 요청하고 상태를 확인할 수 있습니다.",
    },
    {
        "name": "analysis",
        "description": "감성 분석 및 키워드 추출 결과를 조회하는 엔드포인트입니다. 다양한 필터링 옵션과 집계 기능을 제공합니다.",
    },
    {
        "name": "notifications",
        "description": "시스템 알림 및 이벤트를 관리하는 엔드포인트입니다.",
    },
    {
        "name": "admin",
        "description": "관리자 기능을 위한 엔드포인트입니다. 시스템 설정 및 사용자 관리 기능을 제공합니다.",
    },
    {
        "name": "health",
        "description": "시스템 상태 및 헬스체크를 위한 엔드포인트입니다.",
    },
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 이벤트 핸들러"""
    # 시작 시 실행
    print(f"SweetSpot API 서버가 시작되었습니다. (환경: {os.getenv('ENVIRONMENT', 'development')})")
    print(f"API 문서: http://localhost:8000{settings.API_V1_STR}/docs")
    print(f"ReDoc 문서: http://localhost:8000{settings.API_V1_STR}/redoc")
    
    yield
    
    # 종료 시 실행
    print("SweetSpot API 서버가 종료되었습니다.")

app = FastAPI(
    title="SweetSpot API",
    description="""
    # SweetSpot API

    편의점 디저트 제품에 대한 고객 피드백 분석 시스템 API 문서입니다.
    
    ## 주요 기능
    
    * **YouTube 데이터 수집**: 편의점 디저트 관련 YouTube 동영상 및 댓글 수집
    * **감성 분석**: 수집된 댓글에 대한 감성 분석 (긍정/부정/중립)
    * **키워드 추출**: 중요 키워드 및 주제 추출
    * **대시보드**: 분석 결과 시각화 및 통계 제공
    
    ## 인증
    
    일부 API 엔드포인트는 인증이 필요할 수 있습니다. 인증이 필요한 경우 API 키를 헤더에 포함시켜야 합니다.
    
    ```
    X-API-Key: your_api_key_here
    ```
    """,
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=None,  # 커스텀 독스 URL 사용
    redoc_url=None,  # 커스텀 리독 URL 사용
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    contact={
        "name": "SweetSpot 개발팀",
        "email": "support@sweetspot.example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_STR)

# 정적 파일 디렉토리 설정
static_files_dir = os.path.join(os.getcwd(), "data")
if not os.path.exists(static_files_dir):
    os.makedirs(static_files_dir, exist_ok=True)

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory=static_files_dir), name="static")

# 커스텀 Swagger UI 엔드포인트
@app.get(f"{settings.API_V1_STR}/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=None,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
        swagger_favicon_url="/static/favicon.ico",
    )

# 커스텀 ReDoc 엔드포인트
@app.get(f"{settings.API_V1_STR}/redoc", include_in_schema=False)
async def custom_redoc_html():
    return get_redoc_html(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
        redoc_favicon_url="/static/favicon.ico",
    )

# 루트 경로 리다이렉트
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url=f"{settings.API_V1_STR}/docs")

# 헬스체크 엔드포인트 리다이렉트
@app.get("/health", include_in_schema=False)
async def health_check_redirect():
    return RedirectResponse(url=f"{settings.API_V1_STR}/health")

# 미들웨어 설정
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Server-Name"] = "SweetSpot API"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 