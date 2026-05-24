# db/indexes/events.py

from pymongo import ASCENDING, DESCENDING, IndexModel

EVENTS_INDEXES = [
    # Reconstrucción de sesiones: todos los eventos de un usuario+contenido en orden
    IndexModel(
        [
            ("subscriber_id", ASCENDING),
            ("customer_id", ASCENDING),
            ("date", ASCENDING),
        ],
        name="idx_events_session_rebuild",
    ),
    # Queries por ventana de tiempo (alertas, actividad reciente)
    IndexModel([("date", DESCENDING)], name="idx_events_date"),
    # Filtros de QoE: buffering / rebuffering por fecha
    IndexModel(
        [("type_event", ASCENDING), ("date", DESCENDING)],
        name="idx_events_type_date",
    ),
    # Rankings de contenido
    IndexModel(
        [("customer_id", ASCENDING), ("type_event", ASCENDING)],
        name="idx_events_content_type",
    ),
    # Breakdown por plataforma
    IndexModel([("device_type", ASCENDING)], name="idx_events_device"),
]
