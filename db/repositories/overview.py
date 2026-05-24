# db/repositories/overview.py

import hashlib

from motor.motor_asyncio import AsyncIOMotorDatabase

from config.constants import (
    COLLECTION_SESSIONS,
    COLLECTION_STATS,
    COUNTRY_CENTROIDS,
    DEFAULT_CENTROID,
)


async def get_unique_users(db: AsyncIOMotorDatabase) -> int:
    result = await db[COLLECTION_SESSIONS].distinct("subscriber_id")
    return len(result)


async def get_total_plays(db: AsyncIOMotorDatabase) -> int:
    """Total de reproducciones = número de sesiones de reproducción."""
    return await db[COLLECTION_SESSIONS].count_documents({})


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


async def get_top_content(db: AsyncIOMotorDatabase, limit: int = 10) -> list[dict]:
    """
    Contenidos más vistos. Agrupa content_stats por título (un customer_id es
    una pieza puntual; el título agrupa episodios/repeticiones del mismo show).
    """
    pipeline = [
        {
            "$group": {
                "_id": "$title",
                "total_plays": {"$sum": "$total_plays"},
                "unique_viewers": {"$sum": "$unique_viewers"},
                "content_type": {"$first": "$content_type"},
            }
        },
        {"$sort": {"total_plays": -1}},
        {"$limit": limit},
        {
            "$project": {
                "_id": 0,
                "title": "$_id",
                "total_plays": 1,
                "unique_viewers": 1,
                "content_type": 1,
            }
        },
    ]
    return await db[COLLECTION_STATS].aggregate(pipeline).to_list(length=None)


def _jitter(seed: str, spread: float = 2.5) -> tuple[float, float]:
    """
    Offset (lat, lon) determinístico a partir del subscriber_id, para que los
    usuarios de un mismo país no se apilen exactamente en el centroide.
    Mismo usuario → mismo punto siempre (estable entre requests).
    """
    h = hashlib.md5(seed.encode()).hexdigest()
    lat_off = (int(h[:8], 16) / 0xFFFFFFFF - 0.5) * 2 * spread
    lon_off = (int(h[8:16], 16) / 0xFFFFFFFF - 0.5) * 2 * spread
    return lat_off, lon_off


async def get_users_map(db: AsyncIOMotorDatabase, limit: int = 800) -> list[dict]:
    """
    Una burbuja por usuario activo, ubicada en el centroide de su país + jitter.
    El tamaño de la burbuja en el frontend escala con el número de sesiones.
    """
    pipeline = [
        {
            "$group": {
                "_id": "$subscriber_id",
                "sessions": {"$sum": 1},
                "country_code": {"$first": "$country_code"},
                "total_buffer_time": {"$sum": "$total_buffer_time"},
            }
        },
        {"$sort": {"sessions": -1}},
        {"$limit": limit},
    ]
    rows = await db[COLLECTION_SESSIONS].aggregate(pipeline).to_list(length=None)

    points = []
    for r in rows:
        sub = r["_id"]
        country = (r.get("country_code") or "CO").upper()
        base_lat, base_lon = COUNTRY_CENTROIDS.get(country, DEFAULT_CENTROID)
        lat_off, lon_off = _jitter(sub)
        points.append(
            {
                "subscriber_id": sub[:8],  # solo prefijo, no exponer el id completo
                "country_code": country,
                "lat": round(base_lat + lat_off, 4),
                "lon": round(base_lon + lon_off, 4),
                "sessions": r["sessions"],
                "total_buffer_time": round(r.get("total_buffer_time") or 0.0, 2),
            }
        )
    return points
