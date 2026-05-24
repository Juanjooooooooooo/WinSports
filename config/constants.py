APP_NAME = "WinSports"
APP_VERSION = "0.1.0"
APP_DESCRIPTION = "Plataforma de streaming deportivo — métricas y analítica"

# Paginación por defecto
DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 500

# Colecciones MongoDB
COLLECTION_EVENTS = "events"
COLLECTION_SESSIONS = "sessions"
COLLECTION_STATS = "content_stats"

# Centroides (lat, lon) por código de país — para el mapa de usuarios activos.
# El dataset solo trae CountryCode, así que ubicamos cada usuario en el centroide
# de su país + un jitter determinístico (ver repositories/overview.py).
COUNTRY_CENTROIDS = {
    "CO": (4.5709, -74.2973),   # Colombia
    "ES": (40.4637, -3.7492),   # España
    "US": (37.0902, -95.7129),  # Estados Unidos
    "MX": (23.6345, -102.5528),  # México
    "AR": (-38.4161, -63.6167),  # Argentina
    "PE": (-9.1900, -75.0152),  # Perú
    "CL": (-35.6751, -71.5430),  # Chile
    "EC": (-1.8312, -78.1834),  # Ecuador
    "VE": (6.4238, -66.5897),   # Venezuela
    "BR": (-14.2350, -51.9253),  # Brasil
    "UY": (-32.5228, -55.7658),  # Uruguay
    "PA": (8.5380, -80.7821),   # Panamá
    "CR": (9.7489, -83.7534),   # Costa Rica
}
DEFAULT_CENTROID = (4.5709, -74.2973)  # Colombia (mercado principal de Win Sports)
