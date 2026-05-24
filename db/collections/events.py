# db/collections/events.py
#
# Colección `events` — fuente de verdad. Un documento por evento del CSV.
# Raw log, no se modifica después de insertarse.
#
# Decisiones:
# - validationAction="warn": durante la carga masiva (millones de filas) un
#   documento con un campo inesperado NO debe detener el batch. Se loguea y sigue.
# - NO se usa additionalProperties:False: los eventos de streaming tienen esquema
#   flexible (buffer_time solo en buffering, episode/season solo en series).
# - Los enteros aceptan ["int", "long"] porque bitrate/position pueden superar
#   el rango de int32 en el dataset completo.

from motor.motor_asyncio import AsyncIOMotorDatabase

from config.constants import COLLECTION_EVENTS
from db.indexes.events import EVENTS_INDEXES

_INT = ["int", "long", "null"]

EVENTS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "date",
            "subscriber_id",
            "customer_id",
            "type_event",
            "device_type",
        ],
        "properties": {
            # ── Obligatorios ──────────────────────────────────────────────
            "date": {"bsonType": "date"},
            "subscriber_id": {"bsonType": "string"},
            "customer_id": {"bsonType": "string"},
            "type_event": {"bsonType": "string"},
            "device_type": {"bsonType": "string", "enum": ["ANDR", "IOS", "WEB"]},
            # ── Geografía ─────────────────────────────────────────────────
            "country_code": {"bsonType": ["string", "null"]},
            # ── Contenido ─────────────────────────────────────────────────
            "content_type": {"bsonType": ["string", "null"]},
            "title": {"bsonType": ["string", "null"]},
            "episode": {"bsonType": _INT},
            "series_title": {"bsonType": ["string", "null"]},
            "release_year": {"bsonType": _INT},
            "duration": {"bsonType": _INT},
            "season": {"bsonType": _INT},
            "genres": {"bsonType": ["string", "null"]},
            # ── Reproducción ──────────────────────────────────────────────
            "position": {"bsonType": _INT},
            "language": {"bsonType": ["string", "null"]},
            "bitrate": {"bsonType": _INT},
            "buffer_time": {"bsonType": ["double", "int", "null"]},
            "playback_net_time": {"bsonType": _INT},
            # ── Metadata de dispositivo / clasificación ───────────────────
            "device_description": {"bsonType": ["string", "null"]},
            "calc_program_type": {"bsonType": ["string", "null"]},
            "calc_bitrate_type": {"bsonType": ["string", "null"]},
        },
    }
}


async def setup_events_collection(db: AsyncIOMotorDatabase) -> None:
    """
    Crea la colección `events` con su validator e índices.
    Si ya existe, re-aplica el validator vía collMod (idempotente).
    """
    existing = await db.list_collection_names()

    if COLLECTION_EVENTS not in existing:
        await db.create_collection(
            COLLECTION_EVENTS,
            validator=EVENTS_VALIDATOR,
            validationLevel="moderate",
            validationAction="warn",
        )
        print("✅ Colección 'events' creada.")
    else:
        await db.command(
            "collMod",
            COLLECTION_EVENTS,
            validator=EVENTS_VALIDATOR,
            validationLevel="moderate",
            validationAction="warn",
        )
        print("ℹ️  'events' ya existe — validator re-aplicado.")

    await db[COLLECTION_EVENTS].create_indexes(EVENTS_INDEXES)
    print("✅ Índices de 'events' listos.")
