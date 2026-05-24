from pydantic import BaseModel


class UniqueUsersResponse(BaseModel):
    total: int


class TotalPlaysResponse(BaseModel):
    total: int


class DeviceRankingItem(BaseModel):
    device: str
    sessions: int


class DeviceRankingResponse(BaseModel):
    devices: list[DeviceRankingItem]


class ActivityByHourItem(BaseModel):
    hour: int
    sessions: int


class ActivityByHourResponse(BaseModel):
    activity: list[ActivityByHourItem]


class TopContentItem(BaseModel):
    title: str | None
    total_plays: int
    unique_viewers: int | None = None
    content_type: str | None = None


class TopContentResponse(BaseModel):
    content: list[TopContentItem]


class UsersMapPoint(BaseModel):
    subscriber_id: str
    country_code: str
    lat: float
    lon: float
    sessions: int
    total_buffer_time: float


class UsersMapResponse(BaseModel):
    points: list[UsersMapPoint]
