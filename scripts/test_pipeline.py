# scripts/test_pipeline.py

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv()

from motor.motor_asyncio import AsyncIOMotorClient

from config.constants import (
    COLLECTION_EVENTS,
    COLLECTION_SESSIONS,
    COLLECTION_STATS,
)
from config.settings import settings
from db.collections.content_stats import setup_content_stats_collection
from db.collections.sessions import setup_sessions_collection
from db.pipelines.content_stats import build_content_stats_from_db
from db.pipelines.sessions import build_sessions_from_db


async def hard_reset(db) -> None:
    print("\n⚠️  --HARD activado: borrando todas las colecciones...")
    for col in [COLLECTION_SESSIONS, COLLECTION_STATS]:
        await db[col].drop()
        print(f"   🗑️  '{col}' borrada.")


async def main(hard: bool) -> None:
    print("🚀 WinSports — Test Pipeline")

    client = AsyncIOMotorClient(settings.mongo_uri)
    db = client[settings.mongo_db_name]

    if hard:
        await hard_reset(db)

    # Setup de colecciones
    print("\n⚙️  Configurando colecciones...")
    await setup_sessions_collection(db)
    await setup_content_stats_collection(db)

    # Contar eventos disponibles
    event_count = await db[COLLECTION_EVENTS].count_documents({})
    print(f"\n📊 Eventos en Atlas: {event_count:,}")

    if event_count == 0:
        print("⚠️  No hay eventos cargados. Sube el CSV primero.")
        client.close()
        return

    # Construir sesiones
    print("\n🔧 Construyendo sesiones...")
    result = await build_sessions_from_db(db)
    print(f"   Procesadas: {result['processed']:,}")
    print(f"   Insertadas: {result['upserted']:,}")
    print(f"   Actualizadas: {result['modified']:,}")

    # Construir content_stats
    print("\n🔧 Construyendo content_stats...")
    result = await build_content_stats_from_db(db)
    print(f"   Procesadas: {result['processed']:,}")
    print(f"   Insertadas: {result['upserted']:,}")
    print(f"   Actualizadas: {result['modified']:,}")

    # Verificación rápida
    print("\n✅ Verificación final:")
    print(
        f"   sessions:      {await db[COLLECTION_SESSIONS].count_documents({}):,} documentos"
    )
    print(
        f"   content_stats: {await db[COLLECTION_STATS].count_documents({}):,} documentos"
    )

    client.close()
    print("\n🎉 Listo.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test del pipeline de WinSports")
    parser.add_argument(
        "--HARD",
        action="store_true",
        help="Borra todas las colecciones antes de correr",
    )
    args = parser.parse_args()

    asyncio.run(main(args.HARD))
