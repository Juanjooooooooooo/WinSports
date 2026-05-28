from datetime import datetime, timedelta, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

from config.constants import COLLECTION_EVENTS, COLLECTION_SESSIONS


async def _get_data_window(db) -> tuple:
    latest = await db[COLLECTION_EVENTS].find_one(
        {}, {"date": 1, "_id": 0}, sort=[("date", -1)]
    )
    earliest = await db[COLLECTION_EVENTS].find_one(
        {}, {"date": 1, "_id": 0}, sort=[("date", 1)]
    )
    return earliest["date"], latest["date"]


async def get_buffer_alerts(db: AsyncIOMotorDatabase) -> list[dict]:
    """
    Roja — sesiones donde total_buffer_time > 15s en la última hora.
    """
    start, end = await _get_data_window(db)

    cursor = (
        db[COLLECTION_SESSIONS]
        .find(
            {
                "start_time": {"$gte": start, "$lte": end},
                "total_buffer_time": {"$gt": 15},
            },
            {
                "_id": 0,
                "subscriber_id": 1,
                "customer_id": 1,
                "title": 1,
                "total_buffer_time": 1,
                "start_time": 1,
                "device_type": 1,
            },
        )
        .sort("total_buffer_time", -1)
    )

    results = await cursor.to_list(length=None)

    return [
        {
            "severity": "red",
            "type": "buffer_critico",
            "description": f"{r['title'] or r['customer_id']} — {r['total_buffer_time']}s de buffer acumulado",
            "subscriber_id": r["subscriber_id"],
            "device_type": r.get("device_type"),
            "timestamp": r["start_time"],
        }
        for r in results
    ]


async def get_rebuffer_rate_alerts(db: AsyncIOMotorDatabase) -> list[dict]:
    """
    Amarilla — contenidos donde >30% de sesiones en la última hora
    tienen al menos 1 RE-BUFFERING.
    """
    start, end = await _get_data_window(db)

    pipeline = [
        {"$match": {"start_time": {"$gte": start, "$lte": end}}},
        {
            "$group": {
                "_id": "$customer_id",
                "title": {"$first": "$title"},
                "total": {"$sum": 1},
                "with_rebuffer": {
                    "$sum": {"$cond": [{"$gt": ["$rebuffer_count", 0]}, 1, 0]}
                },
            }
        },
        {
            "$project": {
                "_id": 0,
                "customer_id": "$_id",
                "title": 1,
                "total": 1,
                "with_rebuffer": 1,
                "rate": {"$divide": ["$with_rebuffer", "$total"]},
            }
        },
        {"$match": {"rate": {"$gt": 0.30}, "total": {"$gte": 10}}},
        {"$sort": {"rate": -1}},
    ]

    results = await db[COLLECTION_SESSIONS].aggregate(pipeline).to_list(length=None)

    return [
        {
            "severity": "yellow",
            "type": "rebuffer_rate",
            "description": f"{r['title'] or r['customer_id']} — {round(r['rate'] * 100, 1)}% de sesiones con re-buffering",
            "customer_id": r["customer_id"],
            "total_sessions": r["total"],
            "timestamp": start,
        }
        for r in results
    ]


async def get_pause_storm_alerts(db: AsyncIOMotorDatabase) -> list[dict]:
    """
    Azul — usuarios con >5 PAUSEs en menos de 8 minutos en una misma sesión.
    """
    start, end = await _get_data_window(db)
    window = timedelta(minutes=8)

    cursor = (
        db[COLLECTION_EVENTS]
        .find(
            {
                "type_event": "PAUSE",
                "date": {"$gte": start, "$lte": end},
            },
            {"_id": 0, "subscriber_id": 1, "customer_id": 1, "date": 1, "title": 1},
        )
        .sort([("subscriber_id", 1), ("customer_id", 1), ("date", 1)])
    )

    events = await cursor.to_list(length=None)

    # Agrupar por (subscriber_id, customer_id) y buscar ventanas con >5 PAUSEs
    from collections import defaultdict

    groups = defaultdict(list)
    for ev in events:
        key = (ev["subscriber_id"], ev["customer_id"])
        groups[key].append(ev)

    alerts = []
    for (subscriber_id, customer_id), pauses in groups.items():
        for i, pause in enumerate(pauses):
            window_pauses = [
                p for p in pauses[i:] if p["date"] - pause["date"] <= window
            ]
            if len(window_pauses) > 5:
                alerts.append(
                    {
                        "severity": "blue",
                        "type": "pause_storm",
                        "description": f"{window_pauses[0].get('title') or customer_id} — {len(window_pauses)} pausas en menos de 8 minutos",
                        "subscriber_id": subscriber_id,
                        "timestamp": pause["date"],
                    }
                )
                break  # una alerta por usuario+contenido

    return alerts


async def get_all_alerts(db: AsyncIOMotorDatabase) -> dict:
    """
    Combina las tres alertas ordenadas por severidad y timestamp.
    """
    severity_order = {"red": 0, "yellow": 1, "blue": 2}

    start, end = await _get_data_window(db)

    buffer_alerts = await get_buffer_alerts(db)
    rebuffer_alerts = await get_rebuffer_rate_alerts(db)
    pause_alerts = await get_pause_storm_alerts(db)

    all_alerts = buffer_alerts + rebuffer_alerts + pause_alerts
    all_alerts.sort(key=lambda a: (severity_order[a["severity"]], a["timestamp"]))

    return {
        "alerts": all_alerts,
        "period_start": start,
        "period_end": end,
    }
