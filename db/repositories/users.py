# db/repositories/users.py

from motor.motor_asyncio import AsyncIOMotorDatabase

from config.constants import COLLECTION_SESSIONS, COLLECTION_STATS


async def get_retention_funnel(db: AsyncIOMotorDatabase) -> dict:
    total = await db[COLLECTION_SESSIONS].count_documents({})

    firstquartile = await db[COLLECTION_SESSIONS].count_documents(
        {"reached_firstquartile": True}
    )
    midpoint = await db[COLLECTION_SESSIONS].count_documents({"reached_midpoint": True})
    thirdquartile = await db[COLLECTION_SESSIONS].count_documents(
        {"reached_thirdquartile": True}
    )
    complete = await db[COLLECTION_SESSIONS].count_documents({"reached_complete": True})

    return {
        "total": total,
        "firstquartile": firstquartile,
        "midpoint": midpoint,
        "thirdquartile": thirdquartile,
        "complete": complete,
    }


async def get_activity_heatmap(db: AsyncIOMotorDatabase) -> list[dict]:
    pipeline = [
        {
            "$group": {
                "_id": {
                    "hour": {"$hour": "$start_time"},
                    "weekday": {"$dayOfWeek": "$start_time"},
                },
                "sessions": {"$sum": 1},
            }
        },
        {
            "$project": {
                "_id": 0,
                "hour": "$_id.hour",
                "weekday": "$_id.weekday",  # 1=domingo, 7=sábado (Mongo convention)
                "sessions": 1,
            }
        },
    ]
    result = await db[COLLECTION_SESSIONS].aggregate(pipeline).to_list(length=None)

    # Garantizar los 168 puntos (24h × 7 días) aunque algunos tengan 0
    lookup = {(r["weekday"], r["hour"]): r["sessions"] for r in result}
    full = []
    for day in range(1, 8):
        for hour in range(24):
            full.append(
                {"weekday": day, "hour": hour, "sessions": lookup.get((day, hour), 0)}
            )
    return full


async def get_content_completion_ranking(
    db: AsyncIOMotorDatabase, min_plays: int = 5
) -> dict:
    pipeline = [
        # Agrupar por title, sumando plays y promediando completion_rate
        {
            "$group": {
                "_id": "$title",
                "total_plays": {"$sum": "$total_plays"},
                "completion_rate": {"$avg": "$completion_rate"},
            }
        },
        # Filtrar por mínimo de plays después de agrupar
        {"$match": {"total_plays": {"$gte": min_plays}}},
        {"$sort": {"completion_rate": -1}},
        {
            "$project": {
                "_id": 0,
                "title": "$_id",
                "total_plays": 1,
                "completion_rate": {"$round": ["$completion_rate", 1]},
            }
        },
    ]
    result = await db[COLLECTION_STATS].aggregate(pipeline).to_list(length=None)

    return {
        "most_completed": result[:5],
        "most_abandoned": list(reversed(result[-5:])) if len(result) >= 5 else [],
    }


async def get_user_profiles(db: AsyncIOMotorDatabase) -> dict:
    pipeline = [
        {"$group": {"_id": "$subscriber_id", "sessions": {"$sum": 1}}},
        {
            "$project": {
                "_id": 0,
                "profile": {
                    "$switch": {
                        "branches": [
                            {"case": {"$lt": ["$sessions", 3]}, "then": "Casual"},
                            {"case": {"$lte": ["$sessions", 10]}, "then": "Regular"},
                        ],
                        "default": "Heavy",
                    }
                },
            }
        },
        {"$group": {"_id": "$profile", "count": {"$sum": 1}}},
        {
            "$project": {
                "_id": 0,
                "profile": "$_id",
                "count": 1,
            }
        },
    ]
    result = await db[COLLECTION_SESSIONS].aggregate(pipeline).to_list(length=None)

    # Garantizar los tres perfiles aunque alguno tenga 0
    lookup = {r["profile"]: r["count"] for r in result}
    return {
        "profiles": [
            {"profile": "Casual", "count": lookup.get("Casual", 0)},
            {"profile": "Regular", "count": lookup.get("Regular", 0)},
            {"profile": "Heavy", "count": lookup.get("Heavy", 0)},
        ]
    }
