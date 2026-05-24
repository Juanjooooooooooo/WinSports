# api/routes/users.py

from fastapi import APIRouter, Depends, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from api.schemas.users import (
    ActivityHeatmapResponse,
    ContentCompletionRankingResponse,
    RetentionFunnelResponse,
    UserProfilesResponse,
)
from db.connection import get_db
from db.repositories.users import (
    get_activity_heatmap,
    get_content_completion_ranking,
    get_retention_funnel,
    get_user_profiles,
)

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/retention-funnel", response_model=RetentionFunnelResponse)
async def retention_funnel(db: AsyncIOMotorDatabase = Depends(get_db)):
    result = await get_retention_funnel(db)
    return RetentionFunnelResponse(**result)


@router.get("/activity-heatmap", response_model=ActivityHeatmapResponse)
async def activity_heatmap(db: AsyncIOMotorDatabase = Depends(get_db)):
    activity = await get_activity_heatmap(db)
    return ActivityHeatmapResponse(activity=activity)


@router.get(
    "/content-completion-ranking", response_model=ContentCompletionRankingResponse
)
async def content_completion_ranking(
    min_plays: int = Query(default=5, ge=1), db: AsyncIOMotorDatabase = Depends(get_db)
):
    result = await get_content_completion_ranking(db, min_plays)
    return ContentCompletionRankingResponse(**result)


@router.get("/user-profiles", response_model=UserProfilesResponse)
async def user_profiles(db: AsyncIOMotorDatabase = Depends(get_db)):
    result = await get_user_profiles(db)
    return UserProfilesResponse(**result)
