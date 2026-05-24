from pymongo import ASCENDING, DESCENDING, IndexModel

SESSIONS_INDEXES = [
    # Usuarios únicos y perfil de usuario
    IndexModel([("subscriber_id", ASCENDING)], name="idx_sessions_subscriber"),
    # Queries por contenido
    IndexModel([("customer_id", ASCENDING)], name="idx_sessions_content"),
    # Ranking de dispositivos
    IndexModel([("device_type", ASCENDING)], name="idx_sessions_device"),
    # Alertas: sesiones recientes con buffer alto
    IndexModel(
        [("start_time", DESCENDING), ("total_buffer_time", DESCENDING)],
        name="idx_sessions_time_buffer",
    ),
    # Funnel de retención por contenido
    IndexModel(
        [("customer_id", ASCENDING), ("reached_complete", ASCENDING)],
        name="idx_sessions_content_complete",
    ),
    # Crear "FOREIGN_KEYS_UNICAS"
    IndexModel(
        [
            ("subscriber_id", ASCENDING),
            ("customer_id", ASCENDING),
            ("start_time", ASCENDING),
        ],
        name="idx_sessions_unique_key",
        unique=True,
    ),
]
