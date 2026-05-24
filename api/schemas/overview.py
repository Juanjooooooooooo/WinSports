from pydantic import BaseModel


class UniqueUsersResponse(BaseModel):
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
