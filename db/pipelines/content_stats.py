# db/pipelines/content_stats.py

from collections import defaultdict
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import UpdateOne

from config.constants import COLLECTION_SESSIONS, COLLECTION_STATS


def _build_content_stats(sessions: list[dict]) -> list[dict]:
    groups: dict[str, list] = defaultdict(list)
    for s in sessions:
        groups[s["customer_id"]].append(s)

    docs = []

    for customer_id, sess_list in groups.items():
        n = len(sess_list)
        first = sess_list[0]

        # Volumen
        unique_viewers = len({s["subscriber_id"] for s in sess_list})

        # Funnel
        def rate(field):
            return round(sum(1 for s in sess_list if s.get(field)) / n * 100, 2)

        # QoE
        buffers = [
            s["total_buffer_time"]
            for s in sess_list
            if s.get("total_buffer_time") is not None
        ]
        avg_buffer = round(sum(buffers) / len(buffers), 3) if buffers else 0.0

        rebuffer_sessions = sum(1 for s in sess_list if s.get("rebuffer_count", 0) > 0)
        rebuffer_rate = round(rebuffer_sessions / n * 100, 2)

        completions = [
            s["completion_pct"]
            for s in sess_list
            if s.get("completion_pct") is not None
        ]
        avg_completion_pct = (
            round(sum(completions) / len(completions), 2) if completions else None
        )

        # Breakdown por dispositivo
        device_counts: dict[str, int] = {}
        for s in sess_list:
            dt = s.get("device_type")
            if dt:
                device_counts[dt] = device_counts.get(dt, 0) + 1

        docs.append(
            {
                "customer_id": customer_id,
                "title": first.get("title"),
                "series_title": first.get("series_title"),
                "content_type": first.get("content_type"),
                "genres": first.get("genres"),
                "release_year": first.get("release_year"),
                "duration": first.get("duration"),
                "total_plays": n,
                "unique_viewers": unique_viewers,
                "firstquartile_rate": rate("reached_firstquartile"),
                "midpoint_rate": rate("reached_midpoint"),
                "thirdquartile_rate": rate("reached_thirdquartile"),
                "completion_rate": rate("reached_complete"),
                "avg_buffer_time": avg_buffer,
                "rebuffer_rate": rebuffer_rate,
                "avg_completion_pct": avg_completion_pct,
                "plays_by_device": device_counts,
                "last_updated": datetime.now(timezone.utc),
            }
        )

    return docs


async def build_content_stats_from_db(db: AsyncIOMotorDatabase) -> dict:
    cursor = db[COLLECTION_SESSIONS].find(
        {},
        {
            "_id": 0,
            "customer_id": 1,
            "subscriber_id": 1,
            "title": 1,
            "series_title": 1,
            "content_type": 1,
            "genres": 1,
            "release_year": 1,
            "duration": 1,
            "device_type": 1,
            "total_buffer_time": 1,
            "rebuffer_count": 1,
            "completion_pct": 1,
            "reached_firstquartile": 1,
            "reached_midpoint": 1,
            "reached_thirdquartile": 1,
            "reached_complete": 1,
        },
    )

    sessions = await cursor.to_list(length=None)

    if not sessions:
        return {"processed": 0, "upserted": 0, "modified": 0}

    docs = _build_content_stats(sessions)

    operations = [
        UpdateOne({"customer_id": doc["customer_id"]}, {"$set": doc}, upsert=True)
        for doc in docs
    ]

    result = await db[COLLECTION_STATS].bulk_write(operations, ordered=False)

    return {
        "processed": len(docs),
        "upserted": result.upserted_count,
        "modified": result.modified_count,
    }
