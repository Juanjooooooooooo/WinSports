from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from api.schemas.overview import (
    ActivityByHourResponse,
    DeviceRankingResponse,
    TopContentResponse,
    TotalPlaysResponse,
    UniqueUsersResponse,
    UsersMapResponse,
)
from db.connection import get_db
from db.repositories.overview import (
    get_activity_by_hour,
    get_device_ranking,
    get_top_content,
    get_total_plays,
    get_unique_users,
    get_users_map,
)

router = APIRouter(prefix="/api/overview", tags=["Overview"])


@router.get("/unique-users", response_model=UniqueUsersResponse)
async def unique_users(db: AsyncIOMotorDatabase = Depends(get_db)):
    total = await get_unique_users(db)
    return UniqueUsersResponse(total=total)


@router.get("/total-plays", response_model=TotalPlaysResponse)
async def total_plays(db: AsyncIOMotorDatabase = Depends(get_db)):
    total = await get_total_plays(db)
    return TotalPlaysResponse(total=total)


@router.get("/device-ranking", response_model=DeviceRankingResponse)
async def device_ranking(db: AsyncIOMotorDatabase = Depends(get_db)):
    devices = await get_device_ranking(db)
    return DeviceRankingResponse(devices=devices)


@router.get("/activity-by-hour", response_model=ActivityByHourResponse)
async def activity_by_hour(db: AsyncIOMotorDatabase = Depends(get_db)):
    activity = await get_activity_by_hour(db)
    return ActivityByHourResponse(activity=activity)


@router.get("/top-content", response_model=TopContentResponse)
async def top_content(
    limit: int = Query(default=10, ge=1, le=50),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    content = await get_top_content(db, limit)
    return TopContentResponse(content=content)


@router.get("/users-map", response_model=UsersMapResponse)
async def users_map(
    limit: int = Query(default=800, ge=1, le=5000),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    points = await get_users_map(db, limit)
    return UsersMapResponse(points=points)
