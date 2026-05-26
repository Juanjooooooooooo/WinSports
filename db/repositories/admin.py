# db/repositories/admin.py
#
# Operaciones del panel de administración: conteo de colecciones, navegación y
# edición en vivo de documentos, y carga de nuevos CSVs (que re-construye las
# colecciones derivadas).

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase

from config.constants import (
    COLLECTION_EVENTS,
    COLLECTION_SESSIONS,
    COLLECTION_STATS,
)
from db.collections.events import setup_events_collection
from db.csv_ingest import insert_events, parse_records, read_csv_bytes
from db.pipelines.content_stats import build_content_stats_from_db
from db.pipelines.sessions import build_sessions_from_db

# Colecciones que el panel puede inspeccionar y editar. Cualquier otra se rechaza
# en la capa de rutas — el admin no puede tocar colecciones internas de Mongo.
ADMIN_COLLECTIONS = (COLLECTION_EVENTS, COLLECTION_SESSIONS, COLLECTION_STATS)


def _to_object_id(doc_id: str) -> ObjectId:
    try:
        return ObjectId(doc_id)
    except (InvalidId, TypeError) as e:
        raise ValueError(f"ID de documento inválido: {doc_id}") from e


def _stringify_id(doc: dict) -> dict:
    """ObjectId no es serializable a JSON — lo pasamos a string."""
    if doc and isinstance(doc.get("_id"), ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc


async def count_collections(db: AsyncIOMotorDatabase) -> list[dict]:
    """Conteo de documentos de cada colección expuesta al admin."""
    return [
        {"name": name, "count": await db[name].count_documents({})}
        for name in ADMIN_COLLECTIONS
    ]


async def list_documents(
    db: AsyncIOMotorDatabase, collection: str, page: int, page_size: int
) -> dict:
    """Documentos paginados de una colección (para la tabla editable)."""
    total = await db[collection].count_documents({})
    skip = (page - 1) * page_size
    cursor = db[collection].find({}).skip(skip).limit(page_size)
    docs = [_stringify_id(d) for d in await cursor.to_list(length=page_size)]
    return {"total": total, "documents": docs}


async def update_document(
    db: AsyncIOMotorDatabase, collection: str, doc_id: str, fields: dict
) -> int:
    """Edición en vivo: aplica un $set con los campos dados. `_id` es inmutable."""
    oid = _to_object_id(doc_id)
    payload = {k: v for k, v in fields.items() if k != "_id"}
    if not payload:
        return 0
    result = await db[collection].update_one({"_id": oid}, {"$set": payload})
    return result.modified_count


async def delete_document(
    db: AsyncIOMotorDatabase, collection: str, doc_id: str
) -> int:
    oid = _to_object_id(doc_id)
    result = await db[collection].delete_one({"_id": oid})
    return result.deleted_count


async def ingest_csv(db: AsyncIOMotorDatabase, raw: bytes) -> dict:
    """
    Carga un CSV nuevo: asegura la colección `events`, parsea, inserta, y
    re-construye `sessions` y `content_stats` para que el dashboard refleje los
    datos nuevos de inmediato.
    """
    await setup_events_collection(db)

    records = read_csv_bytes(raw)
    clean, total, skipped = parse_records(records)
    inserted, errors = await insert_events(db, clean) if clean else (0, 0)

    sessions = await build_sessions_from_db(db)
    stats = await build_content_stats_from_db(db)

    events_total = await db[COLLECTION_EVENTS].count_documents({})

    return {
        "rows_total": total,
        "rows_skipped": skipped,
        "inserted": inserted,
        "batch_errors": errors,
        "events_total": events_total,
        "sessions_built": sessions["processed"],
        "content_stats_built": stats["processed"],
    }
