from datetime import datetime

from pydantic import BaseModel, field_validator, model_validator

class ResolvedPlanningRequest(BaseModel):
    """The exact time window resolved from a natural-language planning request."""

    window_start: datetime
    window_end: datetime

    @field_validator("window_start", "window_end")
    @classmethod
    def timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Planning-window timestamps must be timezone-aware")
        return value

    @model_validator(mode="after")
    def valid_range(self):
        if self.window_end <= self.window_start:
            raise ValueError("Window end must be later than window start")
        return self
