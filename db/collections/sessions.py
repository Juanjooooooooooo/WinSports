from motor.motor_asyncio import AsyncIOMotorDatabase

from config.constants import COLLECTION_EVENTS, COLLECTION_SESSIONS
from db.indexes.sessions import SESSIONS_INDEXES

SESSIONS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["subscriber_id", "customer_id", "start_time", "device_type"],
        "properties": {
            "subscriber_id": {"bsonType": "string"},
            "customer_id": {"bsonType": "string"},
            "start_time": {"bsonType": "date"},
            "end_time": {"bsonType": ["date", "null"]},
            "device_type": {"bsonType": "string", "enum": ["ANDR", "IOS", "WEB"]},
            "country_code": {"bsonType": ["string", "null"]},
            "title": {"bsonType": ["string", "null"]},
            "series_title": {"bsonType": ["string", "null"]},
            "content_type": {"bsonType": ["string", "null"]},
            "genres": {"bsonType": ["string", "null"]},
            "duration": {"bsonType": ["int", "null"]},
            "total_buffer_time": {"bsonType": ["double", "null"]},
            "rebuffer_count": {"bsonType": ["int", "null"]},
            "pause_count": {"bsonType": ["int", "null"]},
            "max_position": {"bsonType": ["int", "null"]},
            "completion_pct": {"bsonType": ["double", "null"]},
            "reached_firstquartile": {"bsonType": "bool"},
            "reached_midpoint": {"bsonType": "bool"},
            "reached_thirdquartile": {"bsonType": "bool"},
            "reached_complete": {"bsonType": "bool"},
            "dominant_bitrate_type": {"bsonType": ["string", "null"]},
            "event_count": {"bsonType": ["int", "null"]},
        },
    }
}

# db/collections/sessions.py (al final del archivo)


async def setup_sessions_collection(db: AsyncIOMotorDatabase) -> None:
    existing = await db.list_collection_names()

    if COLLECTION_SESSIONS not in existing:
        await db.create_collection(
            COLLECTION_SESSIONS,
            validator=SESSIONS_VALIDATOR,
            validationLevel="moderate",
            validationAction="warn",
        )
        print("✅ Colección 'sessions' creada.")
    else:
        print("ℹ️  'sessions' ya existe.")

    await db[COLLECTION_SESSIONS].create_indexes(SESSIONS_INDEXES)
    print("✅ Índices de 'sessions' listos.")


# db/collections/sessions.py


async def watch_events_and_sync_sessions(db: AsyncIOMotorDatabase) -> None:
    """
    Escucha inserts en 'events' y sincroniza 'sessions' en tiempo real.
    Debe correrse como tarea de fondo al iniciar la API.
    """
    pipeline = [{"$match": {"operationType": "insert"}}]

    async with db[COLLECTION_EVENTS].watch(
        pipeline, full_document="updateLookup"
    ) as stream:
        async for change in stream:
            doc = change["fullDocument"]

            subscriber_id = doc.get("subscriber_id")
            customer_id = doc.get("customer_id")

            if not subscriber_id or not customer_id:
                continue

            # Traer solo los eventos de este usuario+contenido
            cursor = (
                db[COLLECTION_EVENTS]
                .find(
                    {"subscriber_id": subscriber_id, "customer_id": customer_id},
                    {
                        "_id": 0,
                        "subscriber_id": 1,
                        "customer_id": 1,
                        "date": 1,
                        "type_event": 1,
                        "device_type": 1,
                        "country_code": 1,
                        "title": 1,
                        "series_title": 1,
                        "content_type": 1,
                        "genres": 1,
                        "duration": 1,
                        "position": 1,
                        "buffer_time": 1,
                        "calc_bitrate_type": 1,
                    },
                )
                .sort("date", 1)
            )

            events = await cursor.to_list(length=None)

            from db.pipelines.sessions import _build_sessions

            sessions = _build_sessions(events)

            for session in sessions:
                await db[COLLECTION_SESSIONS].update_one(
                    {
                        "subscriber_id": session["subscriber_id"],
                        "customer_id": session["customer_id"],
                        "start_time": session["start_time"],
                    },
                    {"$set": session},
                    upsert=True,
                )
