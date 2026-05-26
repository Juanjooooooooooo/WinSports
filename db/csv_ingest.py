# db/csv_ingest.py
#
# Parseo e ingesta de CSVs de eventos. Lógica compartida entre el script CLI
# (scripts/load_csv.py) y el endpoint de admin (api/routes/admin.py) para que
# ambos casteen, filtren e inserten las filas exactamente igual.

import io
import math
from datetime import datetime, timezone

import pandas as pd
from motor.motor_asyncio import AsyncIOMotorDatabase

from config.constants import COLLECTION_EVENTS

BATCH_SIZE = 1_000

# Campos mínimos que exige el validator de `events`. Una fila sin alguno de
# estos se descarta (no se puede construir una sesión a partir de ella).
REQUIRED_FIELDS = ("date", "subscriber_id", "customer_id", "type_event", "device_type")


def _to_str(val):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    s = str(val).strip()
    return s or None


def _to_int(val):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        # El CSV trae enteros como "2023.0" → castear vía float primero
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return None


def _to_float(val):
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _to_date(val):
    if not val or (isinstance(val, float) and math.isnan(val)):
        return None
    try:
        return datetime.strptime(str(val).strip(), "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
    except (ValueError, TypeError):
        return None


def parse_row(row: dict) -> dict:
    """
    Mapea una fila del CSV a un documento de la colección `events`.
    Los NaN de pandas se convierten en None; los tipos se castean al
    bsonType que espera el validator de events.py.
    """
    return {
        "date": _to_date(row.get("Date")),
        "country_code": _to_str(row.get("CountryCode")),
        "subscriber_id": _to_str(row.get("SubscriberID")),
        "customer_id": _to_str(row.get("CustomerId")),
        "content_type": _to_str(row.get("ContentType")),
        "title": _to_str(row.get("Title")),
        "episode": _to_int(row.get("Episode")),
        "series_title": _to_str(row.get("SeriesTitle")),
        "release_year": _to_int(row.get("ReleaseYear")),
        "duration": _to_int(row.get("Duration")),
        "season": _to_int(row.get("Season")),
        "genres": _to_str(row.get("Genres")),
        "device_type": _to_str(row.get("DeviceType")),
        "type_event": _to_str(row.get("TypeEvent")),
        "position": _to_int(row.get("Position")),
        "language": _to_str(row.get("Language")),
        "bitrate": _to_int(row.get("Bitrate")),
        "buffer_time": _to_float(row.get("BufferTime")),
        "playback_net_time": _to_int(row.get("PlaybackNetTime")),
        "device_description": _to_str(row.get("deviceDescription")),
        "calc_program_type": _to_str(row.get("CALC_ProgramType")),
        "calc_bitrate_type": _to_str(row.get("CALC_BitrateType")),
    }


def parse_records(records: list[dict]) -> tuple[list[dict], int, int]:
    """
    Parsea filas crudas (dicts del CSV) y filtra las que no tienen los campos
    mínimos. Retorna `(docs_limpios, total_leídas, omitidas)`.
    """
    all_docs = [parse_row(r) for r in records]
    clean = [d for d in all_docs if all(d[f] for f in REQUIRED_FIELDS)]
    return clean, len(all_docs), len(all_docs) - len(clean)


def read_csv_bytes(raw: bytes) -> list[dict]:
    """Lee los bytes de un CSV subido y los devuelve como lista de filas."""
    df = pd.read_csv(io.BytesIO(raw), dtype=str)
    return df.to_dict(orient="records")


async def insert_events(db: AsyncIOMotorDatabase, docs: list[dict]) -> tuple[int, int]:
    """
    Inserta documentos en `events` por batches. `ordered=False` deja entrar los
    válidos aunque alguno falle la validación. Retorna `(insertados, batches_con_error)`.
    """
    inserted = 0
    errors = 0
    for i in range(0, len(docs), BATCH_SIZE):
        batch = docs[i : i + BATCH_SIZE]
        try:
            result = await db[COLLECTION_EVENTS].insert_many(batch, ordered=False)
            inserted += len(result.inserted_ids)
        except Exception as e:  # noqa: BLE001
            # BulkWriteError trae el conteo real de insertados en su details
            inserted += getattr(e, "details", {}).get("nInserted", 0)
            errors += 1
    return inserted, errors
