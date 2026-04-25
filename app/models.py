from pydantic import BaseModel, field_validator, Field
from datetime import datetime, timezone
from typing import Literal


class PlantReadingCreate(BaseModel):
    sensor_id: str = Field(..., min_length=1, max_length=50, pattern=r"^[a-zA-Z0-9-]+$")
    moisture: Literal[0, 1]
    status: Literal["wet", "dry"]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    location: str | None = Field(default=None, max_length=100)

    @field_validator("timestamp", mode="before")
    @classmethod
    def default_timestamp(cls, v):
        if v is None:
            return datetime.now(timezone.utc)
        return v


class PlantReadingResponse(BaseModel):
    id: str
    sensor_id: str
    moisture: int
    status: str
    timestamp: datetime
    location: str | None


class SensorResponse(BaseModel):
    sensor_id: str
    name: str | None
    location: str | None
    registered_at: datetime
    last_seen: datetime


class StatsResponse(BaseModel):
    sensor_id: str
    period_hours: int
    total_readings: int
    wet_count: int
    dry_count: int
    dry_percentage: float


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict = {}