from fastapi import APIRouter, Query
from typing import List, Optional
from . import schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.Comment])
async def get_comments(
    sort_by: Optional[str] = Query(None, description="Sort field"),
    order: Optional[str] = Query(None, description="Sort order (asc/desc)"),
    platform: Optional[str] = Query(None, description="Platform filter"),
    sentiment: Optional[str] = Query(None, description="Sentiment filter")
):
    # TODO: Implement comment retrieval with filtering and sorting
    pass 