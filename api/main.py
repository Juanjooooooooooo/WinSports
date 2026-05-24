import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.overview import router as overview_router
from api.routes.users import router as users_router
from config.constants import APP_DESCRIPTION, APP_NAME, APP_VERSION
from config.settings import settings
from db.collections.content_stats import watch_sessions_and_sync_content_stats
from db.collections.sessions import watch_events_and_sync_sessions
from db.connection import connect, disconnect, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect()
    db = get_db()
    asyncio.create_task(watch_events_and_sync_sessions(db))
    asyncio.create_task(watch_sessions_and_sync_content_stats(db))
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

# Registrar routers aquí a medida que se creen
app.include_router(overview_router)
app.include_router(users_router)
