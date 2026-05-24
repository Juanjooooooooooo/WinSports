# api/schemas/users.py

from pydantic import BaseModel


class RetentionFunnelResponse(BaseModel):
    total: int
    firstquartile: int
    midpoint: int
    thirdquartile: int
    complete: int


class HeatmapItem(BaseModel):
    weekday: int
    hour: int
    sessions: int


class ActivityHeatmapResponse(BaseModel):
    activity: list[HeatmapItem]


class ContentCompletionItem(BaseModel):
    title: str
    completion_rate: float
    total_plays: int


class ContentCompletionRankingResponse(BaseModel):
    most_completed: list[ContentCompletionItem]
    most_abandoned: list[ContentCompletionItem]


class UserProfileItem(BaseModel):
    profile: str
    count: int
    total_events: int = 0
    avg_events: float = 0.0
    range: str = ""


class UserProfilesResponse(BaseModel):
    profiles: list[UserProfileItem]
    total_users: int = 0
