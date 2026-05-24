# db/indexes/content_stats.py

from pymongo import ASCENDING, DESCENDING, IndexModel

CONTENT_STATS_INDEXES = [
    # Clave única — un documento por contenido
    IndexModel([("customer_id", ASCENDING)], name="idx_content_stats_id", unique=True),
    # Ranking por vistas
    IndexModel([("total_plays", DESCENDING)], name="idx_content_stats_plays"),
    # Ranking QoE: peores por buffer
    IndexModel([("avg_buffer_time", DESCENDING)], name="idx_content_stats_buffer"),
    # Filtro por género + vistas (para rankings filtrados)
    IndexModel(
        [("genres", ASCENDING), ("total_plays", DESCENDING)],
        name="idx_content_stats_genre",
    ),
    # Agrupación por serie
    IndexModel(
        [("series_title", ASCENDING), ("total_plays", DESCENDING)],
        name="idx_content_stats_series",
    ),
]
