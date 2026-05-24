# db/collections/content_stats.py

from motor.motor_asyncio import AsyncIOMotorDatabase

from config.constants import COLLECTION_SESSIONS, COLLECTION_STATS
from db.indexes.content_stats import CONTENT_STATS_INDEXES

CONTENT_STATS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["customer_id", "title", "total_plays"],
        "properties": {
            "customer_id": {"bsonType": "string"},
            "title": {"bsonType": "string"},
            "series_title": {"bsonType": ["string", "null"]},
            "content_type": {"bsonType": ["string", "null"]},
            "genres": {"bsonType": ["string", "null"]},
            "release_year": {"bsonType": ["int", "null"]},
            "duration": {"bsonType": ["int", "null"]},
            # Volumen
            "total_plays": {"bsonType": "int"},
            "unique_viewers": {"bsonType": ["int", "null"]},
            # Funnel de retención
            "firstquartile_rate": {"bsonType": ["double", "null"]},
            "midpoint_rate": {"bsonType": ["double", "null"]},
            "thirdquartile_rate": {"bsonType": ["double", "null"]},
            "completion_rate": {"bsonType": ["double", "null"]},
            # QoE
            "avg_buffer_time": {"bsonType": ["double", "null"]},
            "rebuffer_rate": {"bsonType": ["double", "null"]},
            "avg_completion_pct": {"bsonType": ["double", "null"]},
            # Breakdown por dispositivo {ANDR: N, IOS: N, WEB: N}
            "plays_by_device": {"bsonType": ["object", "null"]},
            "last_updated": {"bsonType": ["date", "null"]},
        },
    }
}


async def setup_content_stats_collection(db: AsyncIOMotorDatabase) -> None:
    existing = await db.list_collection_names()

    if COLLECTION_STATS not in existing:
        await db.create_collection(
            COLLECTION_STATS,
            validator=CONTENT_STATS_VALIDATOR,
            validationLevel="moderate",
            validationAction="warn",
        )
        print("✅ Colección 'content_stats' creada.")
    else:
        print("ℹ️  'content_stats' ya existe.")

    await db[COLLECTION_STATS].create_indexes(CONTENT_STATS_INDEXES)
    print("✅ Índices de 'content_stats' listos.")


async def watch_sessions_and_sync_content_stats(db: AsyncIOMotorDatabase) -> None:
    pipeline = [{"$match": {"operationType": {"$in": ["insert", "update"]}}}]

    async with db[COLLECTION_SESSIONS].watch(
        pipeline, full_document="updateLookup"
    ) as stream:
        async for change in stream:
            doc = change["fullDocument"]
            customer_id = doc.get("customer_id")

            if not customer_id:
                continue

            # Traer solo sesiones de este contenido
            cursor = db[COLLECTION_SESSIONS].find(
                {"customer_id": customer_id},
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

            from db.pipelines.content_stats import _build_content_stats

            docs = _build_content_stats(sessions)

            if docs:
                await db[COLLECTION_STATS].update_one(
                    {"customer_id": customer_id}, {"$set": docs[0]}, upsert=True
                )
