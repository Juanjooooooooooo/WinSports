import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.constants import APP_DESCRIPTION, APP_NAME, APP_VERSION
from config.settings import settings
from db.collections.sessions import watch_events_and_sync_sessions
from db.connection import connect, disconnect, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect()
    db = get_db()
    asyncio.create_task(watch_events_and_sync_sessions(db))
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
# from api.routes import events, users, streams, metrics
# app.include_router(events.router, prefix="/events", tags=["Events"])
