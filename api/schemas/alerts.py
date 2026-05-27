from datetime import datetime

from pydantic import BaseModel


class AlertItem(BaseModel):
    severity: str
    type: str
    description: str
    timestamp: datetime

    # Opcionales según el tipo de alerta
    subscriber_id: str | None = None
    customer_id: str | None = None
    device_type: str | None = None
    total_sessions: int | None = None


class AlertsResponse(BaseModel):
    alerts: list[AlertItem]
    total_red: int
    total_yellow: int
    total_blue: int
