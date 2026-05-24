# db/repositories/overview.py

from motor.motor_asyncio import AsyncIOMotorDatabase

from config.constants import COLLECTION_SESSIONS


async def get_unique_users(db: AsyncIOMotorDatabase) -> int:
    result = await db[COLLECTION_SESSIONS].distinct("subscriber_id")
    return len(result)


async def get_device_ranking(db: AsyncIOMotorDatabase) -> list[dict]:
    pipeline = [
        {"$group": {"_id": "$device_type", "sessions": {"$sum": 1}}},
        {"$sort": {"sessions": -1}},
        {"$project": {"_id": 0, "device": "$_id", "sessions": 1}},
    ]
    result = await db[COLLECTION_SESSIONS].aggregate(pipeline).to_list(length=None)
    return result


async def get_activity_by_hour(db: AsyncIOMotorDatabase) -> list[dict]:
    pipeline = [
        {"$group": {"_id": {"$hour": "$start_time"}, "sessions": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        {"$project": {"_id": 0, "hour": "$_id", "sessions": 1}},
    ]
    result = await db[COLLECTION_SESSIONS].aggregate(pipeline).to_list(length=None)

    # Garantizar las 24 horas aunque algunas tengan 0 sesiones
    hours = {r["hour"]: r["sessions"] for r in result}
    return [{"hour": h, "sessions": hours.get(h, 0)} for h in range(24)]
