# db/pipelines/sessions.py

from collections import defaultdict

from motor.motor_asyncio import AsyncIOMotorDatabase

from config.constants import COLLECTION_EVENTS, COLLECTION_SESSIONS


def _build_sessions(events: list[dict]) -> list[dict]:
    """
    Lógica pura de construcción de sesiones.
    Recibe eventos ya ordenados por (subscriber_id, customer_id, date)
    y retorna lista de documentos listos para upsert.
    """
    # Agrupar por (subscriber_id, customer_id)
    groups: dict[tuple, list] = defaultdict(list)
    for ev in events:
        key = (ev["subscriber_id"], ev["customer_id"])
        groups[key].append(ev)

    # Ordenar cada grupo por fecha
    for key in groups:
        groups[key].sort(key=lambda e: e["date"])

    sessions = []

    for (subscriber_id, customer_id), evs in groups.items():
        # Partir en sub-sesiones cada vez que aparece un START
        sub_sessions: list[list] = []
        current: list = []

        for ev in evs:
            if ev["type_event"] == "START" and current:
                sub_sessions.append(current)
                current = []
            current.append(ev)

        if current:
            sub_sessions.append(current)

        # Calcular métricas por sub-sesión
        for sub in sub_sessions:
            if not sub:
                continue

            first = sub[0]
            last = sub[-1]
            type_events = {e["type_event"] for e in sub}

            # Buffer
            total_buffer = sum(
                e["buffer_time"] for e in sub if e.get("buffer_time") is not None
            )
            rebuffer_count = sum(1 for e in sub if e["type_event"] == "RE-BUFFERING")
            pause_count = sum(1 for e in sub if e["type_event"] == "PAUSE")

            # Progreso
            positions = [e["position"] for e in sub if e.get("position") is not None]
            max_position = max(positions) if positions else None
            duration = first.get("duration")
            # Cap a 100%: algunas filas traen Position en una unidad distinta a
            # Duration (ms vs s) o posiciones residuales de sesiones previas, lo
            # que dispara el porcentaje por encima de 100. Capear evita que esos
            # outliers contaminen los promedios de completion del dashboard.
            completion_pct = (
                round(min(max_position / duration * 100, 100.0), 2)
                if duration and duration > 0 and max_position is not None
                else None
            )

            # Bitrate dominante
            bitrate_counts: dict[str, int] = {}
            for e in sub:
                bt = e.get("calc_bitrate_type")
                if bt:
                    bitrate_counts[bt] = bitrate_counts.get(bt, 0) + 1
            dominant_bitrate = (
                max(bitrate_counts, key=bitrate_counts.get) if bitrate_counts else None
            )

            sessions.append(
                {
                    "subscriber_id": subscriber_id,
                    "customer_id": customer_id,
                    "start_time": first["date"],
                    "end_time": last["date"],
                    "device_type": first.get("device_type"),
                    "country_code": first.get("country_code"),
                    "title": first.get("title"),
                    "series_title": first.get("series_title"),
                    "content_type": first.get("content_type"),
                    "genres": first.get("genres"),
                    "duration": duration,
                    "total_buffer_time": round(total_buffer, 3),
                    "rebuffer_count": rebuffer_count,
                    "pause_count": pause_count,
                    "max_position": max_position,
                    "completion_pct": completion_pct,
                    "reached_firstquartile": "FIRSTQUARTILE" in type_events,
                    "reached_midpoint": "MIDPOINT" in type_events,
                    "reached_thirdquartile": "THIRDQUARTILE" in type_events,
                    "reached_complete": "COMPLETE" in type_events,
                    "dominant_bitrate_type": dominant_bitrate,
                    "event_count": len(sub),
                }
            )

    return sessions


async def build_sessions_from_db(db: AsyncIOMotorDatabase) -> dict:
    """
    Lee todos los eventos desde Mongo, construye sesiones,
    y hace upsert en la colección sessions.

    Retorna un resumen: cuántas sesiones procesadas, insertadas, actualizadas.
    """
    # Leer todos los eventos ordenados
    cursor = (
        db[COLLECTION_EVENTS]
        .find(
            {},
            {
                # Solo los campos que necesitamos — menos memoria
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
                "_id": 0,
            },
        )
        .sort([("subscriber_id", 1), ("customer_id", 1), ("date", 1)])
    )

    events = await cursor.to_list(length=None)

    if not events:
        return {"processed": 0, "upserted": 0, "modified": 0}

    sessions = _build_sessions(events)

    # Upsert por clave única (subscriber_id + customer_id + start_time)
    upserted = 0
    modified = 0

    for session in sessions:
        result = await db[COLLECTION_SESSIONS].update_one(
            {
                "subscriber_id": session["subscriber_id"],
                "customer_id": session["customer_id"],
                "start_time": session["start_time"],
            },
            {"$set": session},
            upsert=True,
        )
        if result.upserted_id:
            upserted += 1
        elif result.modified_count:
            modified += 1

    return {
        "processed": len(sessions),
        "upserted": upserted,
        "modified": modified,
    }
