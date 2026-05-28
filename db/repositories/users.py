# db/repositories/users.py

from motor.motor_asyncio import AsyncIOMotorDatabase

from config.constants import COLLECTION_EVENTS, COLLECTION_SESSIONS, COLLECTION_STATS

# Umbrales de clasificación de usuarios por número de eventos generados.
# Vague: usuario esporádico · Mid: recurrente · Heavy: muy activo.
PROFILE_MID_MIN = 10
PROFILE_HEAVY_MIN = 50


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
    db: AsyncIOMotorDatabase, min_plays: int = 10
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
    """
    Clasifica a cada usuario por su número total de eventos generados:
      - Vague: < PROFILE_MID_MIN eventos
      - Mid:   entre PROFILE_MID_MIN y PROFILE_HEAVY_MIN - 1
      - Heavy: >= PROFILE_HEAVY_MIN eventos
    """
    pipeline = [
        {"$group": {"_id": "$subscriber_id", "events": {"$sum": 1}}},
        {
            "$project": {
                "_id": 0,
                "events": 1,
                "profile": {
                    "$switch": {
                        "branches": [
                            {
                                "case": {"$lt": ["$events", PROFILE_MID_MIN]},
                                "then": "Vague",
                            },
                            {
                                "case": {"$lt": ["$events", PROFILE_HEAVY_MIN]},
                                "then": "Mid",
                            },
                        ],
                        "default": "Heavy",
                    }
                },
            }
        },
        {
            "$group": {
                "_id": "$profile",
                "count": {"$sum": 1},
                "total_events": {"$sum": "$events"},
                "avg_events": {"$avg": "$events"},
            }
        },
    ]
    result = await db[COLLECTION_EVENTS].aggregate(pipeline).to_list(length=None)
    lookup = {r["_id"]: r for r in result}

    ranges = {
        "Vague": f"< {PROFILE_MID_MIN} eventos",
        "Mid": f"{PROFILE_MID_MIN}–{PROFILE_HEAVY_MIN - 1} eventos",
        "Heavy": f"≥ {PROFILE_HEAVY_MIN} eventos",
    }

    profiles = []
    for name in ("Heavy", "Mid", "Vague"):
        r = lookup.get(name, {})
        profiles.append(
            {
                "profile": name,
                "count": r.get("count", 0),
                "total_events": r.get("total_events", 0),
                "avg_events": round(r.get("avg_events") or 0.0, 1),
                "range": ranges[name],
            }
        )

    return {
        "profiles": profiles,
        "total_users": sum(p["count"] for p in profiles),
    }
