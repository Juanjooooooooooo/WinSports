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


class UserProfilesResponse(BaseModel):
    profiles: list[UserProfileItem]
