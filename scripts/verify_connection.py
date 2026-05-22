# scripts/verify_connection.py
import asyncio
import sys

sys.path.insert(0, ".")  # para que encuentre los módulos desde la raíz

from db.connection import connect, disconnect, get_db


async def verify():
    print("Conectando a Atlas...")
    await connect()

    db = get_db()

    # Esto hace un ping real al servidor
    await db.command("ping")
    print(f"✅ Conexión exitosa — DB: '{db.name}'")

    # Lista las colecciones existentes (vacío si es primera vez)
    collections = await db.list_collection_names()
    print(
        f"   Colecciones encontradas: {collections if collections else '(ninguna aún)'}"
    )

    await disconnect()
    print("Conexión cerrada.")


asyncio.run(verify())
