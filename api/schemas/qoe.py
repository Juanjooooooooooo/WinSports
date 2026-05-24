# api/schemas/qoe.py

from pydantic import BaseModel


class BufferByContentItem(BaseModel):
    title: str | None
    avg_buffer_time: float
    rebuffer_rate: float | None = None
    total_plays: int


class BufferByContentResponse(BaseModel):
    content: list[BufferByContentItem]


class RebufferingRateResponse(BaseModel):
    rebuffer_events: int
    total_events: int
    event_rate: float
    rebuffer_sessions: int
    total_sessions: int
    session_rate: float


class StartupBucket(BaseModel):
    bucket: str
    count: int


class StartupTimeResponse(BaseModel):
    avg_seconds: float
    max_seconds: float
    count: int
    buckets: list[StartupBucket]


class EventRankingItem(BaseModel):
    type_event: str
    count: int


class EventRankingResponse(BaseModel):
    events: list[EventRankingItem]
