from fastapi import APIRouter, Query
from typing import List, Optional
from . import schemas

router = APIRouter()

@router.get("/popular-shorts", response_model=List[schemas.ShortVideo])
async def get_popular_shorts(
    sort_by: Optional[str] = Query(None, description="Sort field")
):
    # TODO: Implement popular shorts retrieval
    pass

@router.get("/popular-videos", response_model=List[schemas.Video])
async def get_popular_videos(
    sort_by: Optional[str] = Query(None, description="Sort field")
):
    # TODO: Implement popular videos retrieval
    pass 