# scripts/load_csv.py

import argparse
import asyncio
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient

from config.constants import COLLECTION_EVENTS
from config.settings import settings
from db.collections.events import setup_events_collection

BATCH_SIZE = 1_000


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


async def main(csv_path: str, hard: bool) -> None:
    print("🚀 WinSports — Carga de CSV")
    print(f"   Archivo: {csv_path}")

    if not Path(csv_path).exists():
        print(f"❌ Archivo no encontrado: {csv_path}")
        return

    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.mongo_db_name]

    if hard:
        print("\n⚠️  --HARD activado: borrando events...")
        await db[COLLECTION_EVENTS].drop()
        print("   🗑️  'events' borrada.")

    # Asegurar que la colección existe con validator + índices antes de insertar
    print("\n⚙️  Configurando colección 'events'...")
    await setup_events_collection(db)

    # Leer CSV
    print("\n📂 Leyendo CSV...")
    df = pd.read_csv(csv_path, dtype=str)
    total = len(df)
    print(f"   {total:,} filas encontradas.")

    # Parsear
    print("⚙️  Parseando filas...")
    all_docs = [parse_row(row) for row in df.to_dict(orient="records")]

    # Filtrar filas sin campos mínimos (los requeridos por el validator)
    clean_docs = [
        d
        for d in all_docs
        if d["date"]
        and d["subscriber_id"]
        and d["customer_id"]
        and d["type_event"]
        and d["device_type"]
    ]
    skipped = total - len(clean_docs)
    if skipped:
        print(f"   ⚠️  {skipped:,} filas omitidas por campos mínimos faltantes.")
    print(f"   ✅ {len(clean_docs):,} documentos listos para insertar.")

    if not clean_docs:
        print("   Nada que insertar.")
        client.close()
        return

    # Insertar en batches
    batches = math.ceil(len(clean_docs) / BATCH_SIZE)
    inserted = 0
    errors = 0

    print(f"\n⬆️  Insertando en {batches} batches de {BATCH_SIZE:,}...")

    for i in range(0, len(clean_docs), BATCH_SIZE):
        batch = clean_docs[i : i + BATCH_SIZE]
        try:
            result = await db[COLLECTION_EVENTS].insert_many(batch, ordered=False)
            inserted += len(result.inserted_ids)
        except Exception as e:
            # ordered=False inserta los válidos aunque alguno falle la validación
            # BulkWriteError trae el conteo real de insertados en su details
            n_ok = getattr(e, "details", {}).get("nInserted", 0)
            inserted += n_ok
            errors += 1
            print(f"\n   ⚠️  Error en batch {i // BATCH_SIZE + 1}: {e}")

        pct = min(i + len(batch), len(clean_docs)) / len(clean_docs) * 100
        print(f"   {pct:5.1f}%  ({inserted:,} insertados)", end="\r")

    print("\n\n✅ Carga completa.")
    print(f"   Insertados: {inserted:,}")
    print(f"   Omitidos:   {skipped:,}")
    if errors:
        print(f"   Batches con error: {errors}")

    print(
        f"\n📊 Total en Atlas: {await db[COLLECTION_EVENTS].count_documents({}):,} eventos"
    )

    client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Carga CSV de eventos a MongoDB Atlas")
    parser.add_argument("--file", required=True, help="Ruta al archivo CSV")
    parser.add_argument(
        "--HARD", action="store_true", help="Borra la colección events antes de cargar"
    )
    args = parser.parse_args()

    asyncio.run(main(args.file, args.HARD))
