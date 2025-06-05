from fastapi import APIRouter
from app.modules.summary.router import router as summary_router
from app.modules.sentiment.router import router as sentiment_router
from app.modules.comments.router import router as comments_router
from app.modules.youtube.router import router as youtube_router
# from app.modules.user.router import router as user_router
from app.modules.search.router import router as search_router

router = APIRouter()

# 각 모듈의 라우터 등록
router.include_router(summary_router, prefix="/summary", tags=["summary"])
router.include_router(sentiment_router, prefix="/sentiment", tags=["sentiment"])
router.include_router(comments_router, prefix="/comments", tags=["comments"])
router.include_router(youtube_router, prefix="/youtube", tags=["youtube"])
# router.include_router(user_router, prefix="/user", tags=["user"])
router.include_router(search_router, prefix="/search", tags=["search"]) 