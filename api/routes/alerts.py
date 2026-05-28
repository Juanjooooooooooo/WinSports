from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from api.schemas.alerts import AlertsResponse
from db.connection import get_db
from db.repositories.alerts import get_all_alerts

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("/", response_model=AlertsResponse)
async def alerts(db: AsyncIOMotorDatabase = Depends(get_db)):
    result = await get_all_alerts(db)

    return AlertsResponse(
        alerts=result["alerts"],
        total_red=sum(1 for a in result["alerts"] if a["severity"] == "red"),
        total_yellow=sum(1 for a in result["alerts"] if a["severity"] == "yellow"),
        total_blue=sum(1 for a in result["alerts"] if a["severity"] == "blue"),
        period_start=result["period_start"],
        period_end=result["period_end"],
    )
