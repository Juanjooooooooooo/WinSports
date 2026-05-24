# scripts/load_csv.py

import argparse
import asyncio
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

import pandas as pd
from motor.motor_asyncio import AsyncIOMotorClient

from config.constants import COLLECTION_EVENTS
from config.settings import settings

BATCH_SIZE = 1_000


def parse_row(row: dict) -> dict:
    """
    Mapea una fila del CSV a un documento de Mongo.
    Los NaN de pandas se convierten en None.
    Los tipos se castean lo mejor posible — validación real
    la hace el validator de events.py cuando esté listo.
    """
    from datetime import datetime, timezone

    def to_str(val):
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return None
        return str(val).strip() or None

    def to_int(val):
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return None
        try:
            return int(val)
        except ValueError, TypeError:
            return None

    def to_float(val):
        if val is None or (isinstance(val, float) and math.isnan(val)):
            return None
        try:
            return float(val)
        except ValueError, TypeError:
            return None

    def to_date(val):
        if not val:
            return None
        try:
            return datetime.strptime(str(val), "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            return None

    return {
        "date": to_date(row.get("Date")),
        "country_code": to_str(row.get("CountryCode")),
        "subscriber_id": to_str(row.get("SubscriberID")),
        "customer_id": to_str(row.get("CustomerId")),
        "content_type": to_str(row.get("ContentType")),
        "title": to_str(row.get("Title")),
        "episode": to_int(row.get("Episode")),
        "series_title": to_str(row.get("SeriesTitle")),
        "release_year": to_int(row.get("ReleaseYear")),
        "duration": to_int(row.get("Duration")),
        "season": to_int(row.get("Season")),
        "genres": to_str(row.get("Genres")),
        "device_type": to_str(row.get("DeviceType")),
        "type_event": to_str(row.get("TypeEvent")),
        "position": to_int(row.get("Position")),
        "language": to_str(row.get("Language")),
        "bitrate": to_int(row.get("Bitrate")),
        "buffer_time": to_float(row.get("BufferTime")),
        "playback_net_time": to_int(row.get("PlaybackNetTime")),
        "device_description": to_str(row.get("deviceDescription")),
        "calc_program_type": to_str(row.get("CALC_ProgramType")),
        "calc_bitrate_type": to_str(row.get("CALC_BitrateType")),
    }


async def main(csv_path: str, hard: bool) -> None:
    print("🚀 WinSports — Carga de CSV")
    print(f"   Archivo: {csv_path}")

    # Verificar que el archivo existe
    if not Path(csv_path).exists():
        print(f"❌ Archivo no encontrado: {csv_path}")
        return

    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.mongo_db_name]

    if hard:
        print("\n⚠️  --HARD activado: borrando events...")
        await db[COLLECTION_EVENTS].drop()
        print("   🗑️  'events' borrada.")

    # Leer CSV
    print("\n📂 Leyendo CSV...")
    df = pd.read_csv(csv_path, dtype=str)
    total = len(df)
    print(f"   {total:,} filas encontradas.")

    # Parsear
    print("⚙️  Parseando filas...")
    all_docs = [parse_row(row) for row in df.to_dict(orient="records")]

    # Filtrar filas sin campos mínimos
    clean_docs = [
        d
        for d in all_docs
        if d["date"] and d["subscriber_id"] and d["customer_id"] and d["type_event"]
    ]
    skipped = total - len(clean_docs)
    if skipped:
        print(f"   ⚠️  {skipped:,} filas omitidas por campos mínimos faltantes.")
    print(f"   ✅ {len(clean_docs):,} documentos listos para insertar.")

    # Insertar en batches
    batches = math.ceil(len(clean_docs) / BATCH_SIZE)
    inserted = 0
    errors = 0

    print(f"\n⬆️  Insertando en {batches} batches de {BATCH_SIZE:,}...")

    for i in range(0, len(clean_docs), BATCH_SIZE):
        batch = clean_docs[i : i + BATCH_SIZE]
        try:
            await db[COLLECTION_EVENTS].insert_many(batch, ordered=False)
            inserted += len(batch)
        except Exception as e:
            # ordered=False significa que inserta los válidos aunque alguno falle
            errors += 1
            print(f"\n   ⚠️  Error en batch {i // BATCH_SIZE + 1}: {e}")

        pct = (
            min(inserted + errors * BATCH_SIZE, len(clean_docs)) / len(clean_docs) * 100
        )
        print(f"   {pct:5.1f}%  ({inserted:,} insertados)", end="\r")

    print(f"\n\n✅ Carga completa.")
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
