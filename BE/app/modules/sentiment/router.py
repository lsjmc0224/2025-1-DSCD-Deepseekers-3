from fastapi import APIRouter, Depends
from typing import List
from . import schemas

router = APIRouter()

@router.get("/overview", response_model=schemas.SentimentOverview)
async def get_sentiment_overview():
    # TODO: Implement sentiment overview analysis
    pass

@router.get("/keywords", response_model=List[schemas.KeywordSentiment])
async def get_sentiment_keywords():
    # TODO: Implement keyword sentiment analysis
    pass 