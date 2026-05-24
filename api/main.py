import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.overview import router as overview_router
from api.routes.qoe import router as qoe_router
from api.routes.users import router as users_router
from config.constants import APP_DESCRIPTION, APP_NAME, APP_VERSION
from config.settings import settings
from db.collections.content_stats import watch_sessions_and_sync_content_stats
from db.collections.sessions import watch_events_and_sync_sessions
from db.connection import connect, disconnect, get_db

logger = logging.getLogger("winsports")


async def _safe_watch(coro_fn, db, name: str) -> None:
    """
    Corre un change-stream watcher tolerando fallos: si el cluster no soporta
    change streams (Mongo standalone, no replica set) o la conexión falla,
    se loguea y se degrada — el resto de la API sigue funcionando con las
    colecciones derivadas que construye test_pipeline.py manualmente.
    """
    try:
        await coro_fn(db)
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "Change stream '%s' deshabilitado (%s). "
            "Usa scripts/test_pipeline.py para construir las derivadas.",
            name,
            e,
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect()
    db = get_db()
    asyncio.create_task(_safe_watch(watch_events_and_sync_sessions, db, "sessions"))
    asyncio.create_task(
        _safe_watch(watch_sessions_and_sync_content_stats, db, "content_stats")
    )
    yield
    await disconnect()


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_dev else [settings.api_base_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["Health"])
async def health():
    """Ping de salud — verifica que la API responde."""
    return {"status": "ok", "app": APP_NAME, "version": APP_VERSION}


# Routers
app.include_router(overview_router)
app.include_router(qoe_router)
app.include_router(users_router)
