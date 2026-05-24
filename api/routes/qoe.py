# api/routes/qoe.py

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from api.schemas.qoe import (
    BufferByContentResponse,
    EventRankingResponse,
    RebufferingRateResponse,
    StartupTimeResponse,
)
from db.connection import get_db
from db.repositories.qoe import (
    get_buffer_by_content,
    get_event_ranking,
    get_rebuffering_rate,
    get_startup_time,
)

router = APIRouter(prefix="/api/qoe", tags=["QoE"])


@router.get("/buffer-by-content", response_model=BufferByContentResponse)
async def buffer_by_content(
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    content = await get_buffer_by_content(db, limit)
    return BufferByContentResponse(content=content)


@router.get("/rebuffering-rate", response_model=RebufferingRateResponse)
async def rebuffering_rate(db: AsyncIOMotorDatabase = Depends(get_db)):
    result = await get_rebuffering_rate(db)
    return RebufferingRateResponse(**result)


@router.get("/startup-time", response_model=StartupTimeResponse)
async def startup_time(db: AsyncIOMotorDatabase = Depends(get_db)):
    result = await get_startup_time(db)
    return StartupTimeResponse(**result)


@router.get("/event-ranking", response_model=EventRankingResponse)
async def event_ranking(db: AsyncIOMotorDatabase = Depends(get_db)):
    events = await get_event_ranking(db)
    return EventRankingResponse(events=events)
