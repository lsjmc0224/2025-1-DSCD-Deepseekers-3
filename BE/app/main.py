from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.api_router import router as api_router

app = FastAPI(
    title="Analysis Backend API",
    description="분석 백엔드 API 서버",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 