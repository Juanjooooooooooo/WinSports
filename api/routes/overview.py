from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from api.schemas.overview import (
    ActivityByHourResponse,
    DeviceRankingResponse,
    UniqueUsersResponse,
)
from db.connection import get_db
from db.repositories.overview import (
    get_activity_by_hour,
    get_device_ranking,
    get_unique_users,
)

router = APIRouter(prefix="/api/overview", tags=["Overview"])


@router.get("/unique-users", response_model=UniqueUsersResponse)
async def unique_users(db: AsyncIOMotorDatabase = Depends(get_db)):
    total = await get_unique_users(db)
    return UniqueUsersResponse(total=total)


@router.get("/device-ranking", response_model=DeviceRankingResponse)
async def device_ranking(db: AsyncIOMotorDatabase = Depends(get_db)):
    devices = await get_device_ranking(db)
    return DeviceRankingResponse(devices=devices)


@router.get("/activity-by-hour", response_model=ActivityByHourResponse)
async def activity_by_hour(db: AsyncIOMotorDatabase = Depends(get_db)):
    activity = await get_activity_by_hour(db)
    return ActivityByHourResponse(activity=activity)
