# db/repositories/qoe.py
#
# Métricas de Quality of Experience (QoE).
# Fuente: `events` (raw) para conteos de eventos y tiempo de inicialización,
# `content_stats` para buffer agregado por contenido.

from motor.motor_asyncio import AsyncIOMotorDatabase

from config.constants import COLLECTION_EVENTS, COLLECTION_SESSIONS, COLLECTION_STATS

# Buckets (en segundos) para la distribución del tiempo de inicialización
_STARTUP_BUCKETS = [
    ("0-1s", 0, 1),
    ("1-2s", 1, 2),
    ("2-5s", 2, 5),
    ("5-10s", 5, 10),
    ("10s+", 10, float("inf")),
]


async def get_buffer_by_content(
    db: AsyncIOMotorDatabase, limit: int = 10
) -> list[dict]:
    """
    Avg buffer time por contenido (los peores primero).
    Agrupa content_stats por título y promedia el buffer por sesión.
    """
    pipeline = [
        {
            "$group": {
                "_id": "$title",
                "avg_buffer_time": {"$avg": "$avg_buffer_time"},
                "rebuffer_rate": {"$avg": "$rebuffer_rate"},
                "total_plays": {"$sum": "$total_plays"},
            }
        },
        {"$match": {"avg_buffer_time": {"$gt": 0}}},
        {"$sort": {"avg_buffer_time": -1}},
        {"$limit": limit},
        {
            "$project": {
                "_id": 0,
                "title": "$_id",
                "avg_buffer_time": {"$round": ["$avg_buffer_time", 3]},
                "rebuffer_rate": {"$round": ["$rebuffer_rate", 2]},
                "total_plays": 1,
            }
        },
    ]
    return await db[COLLECTION_STATS].aggregate(pipeline).to_list(length=None)


async def get_rebuffering_rate(db: AsyncIOMotorDatabase) -> dict:
    """
    Tasa de re-buffering medida de dos formas:
      - sobre eventos:  # eventos RE-BUFFERING / # total de eventos
      - sobre sesiones: # sesiones con ≥1 rebuffer / # total de sesiones
    """
    total_events = await db[COLLECTION_EVENTS].count_documents({})
    rebuffer_events = await db[COLLECTION_EVENTS].count_documents(
        {"type_event": "RE-BUFFERING"}
    )

    total_sessions = await db[COLLECTION_SESSIONS].count_documents({})
    rebuffer_sessions = await db[COLLECTION_SESSIONS].count_documents(
        {"rebuffer_count": {"$gt": 0}}
    )

    return {
        "rebuffer_events": rebuffer_events,
        "total_events": total_events,
        "event_rate": round(rebuffer_events / total_events * 100, 2)
        if total_events
        else 0.0,
        "rebuffer_sessions": rebuffer_sessions,
        "total_sessions": total_sessions,
        "session_rate": round(rebuffer_sessions / total_sessions * 100, 2)
        if total_sessions
        else 0.0,
    }


async def get_startup_time(db: AsyncIOMotorDatabase) -> dict:
    """
    Marcador de tiempo para la inicialización: el buffer_time de los eventos
    START-BUFFERING representa el buffering previo al primer frame (startup).
    Devuelve promedio, máximo, conteo y la distribución por buckets.
    """
    match = {"type_event": "START-BUFFERING", "buffer_time": {"$ne": None}}

    agg = (
        await db[COLLECTION_EVENTS]
        .aggregate(
            [
                {"$match": match},
                {
                    "$group": {
                        "_id": None,
                        "avg": {"$avg": "$buffer_time"},
                        "max": {"$max": "$buffer_time"},
                        "count": {"$sum": 1},
                    }
                },
            ]
        )
        .to_list(length=1)
    )

    stats = agg[0] if agg else {"avg": 0.0, "max": 0.0, "count": 0}

    # Distribución por buckets
    buckets = []
    for label, lo, hi in _STARTUP_BUCKETS:
        cond = {"$gte": lo}
        if hi != float("inf"):
            cond["$lt"] = hi
        q = {**match, "buffer_time": cond}
        # buffer_time != None ya está implícito por el rango numérico
        count = await db[COLLECTION_EVENTS].count_documents(q)
        buckets.append({"bucket": label, "count": count})

    return {
        "avg_seconds": round(stats.get("avg") or 0.0, 3),
        "max_seconds": round(stats.get("max") or 0.0, 3),
        "count": stats.get("count", 0),
        "buckets": buckets,
    }


async def get_event_ranking(db: AsyncIOMotorDatabase) -> list[dict]:
    """Ranking de tipos de evento por frecuencia (sobre la colección events)."""
    pipeline = [
        {"$group": {"_id": "$type_event", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$project": {"_id": 0, "type_event": "$_id", "count": 1}},
    ]
    return await db[COLLECTION_EVENTS].aggregate(pipeline).to_list(length=None)
