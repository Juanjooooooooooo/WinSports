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
from db.collections.events import setup_events_collection

# La lógica de parseo vive en db/csv_ingest.py para compartirla con el endpoint
# de admin. Se re-exporta aquí para no romper imports existentes (tests, etc.).
from db.csv_ingest import (  # noqa: F401
    BATCH_SIZE,
    _to_date,
    _to_float,
    _to_int,
    _to_str,
    parse_row,
)


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
