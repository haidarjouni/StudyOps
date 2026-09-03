from datetime import date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, field_validator, model_validator


def _require_timezone_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Timestamp must be timezone-aware")
    return value


class ResolvedPlanningRequest(BaseModel):
    """The exact time window resolved from a natural-language planning request."""

    window_start: datetime
    window_end: datetime

    @field_validator("window_start", "window_end")
    @classmethod
    def timezone_aware(cls, value: datetime) -> datetime:
        return _require_timezone_aware(value)

    @model_validator(mode="after")
    def valid_range(self):
        if self.window_end <= self.window_start:
            raise ValueError("Window end must be later than window start")
        return self


class DailyPlanningPeriod(BaseModel):
    date: date
    start_at: datetime
    end_at: datetime

    @field_validator("start_at", "end_at")
    @classmethod
    def timezone_aware(cls, value: datetime) -> datetime:
        return _require_timezone_aware(value)

    @model_validator(mode="after")
    def valid_range(self):
        if self.end_at <= self.start_at:
            raise ValueError("Daily period end must be later than its start")
        return self


class PlanningConstraints(BaseModel):
    timezone: str
    window_start: datetime
    window_end: datetime

    preferred_session_minutes: int = Field(gt=0)
    buffer_minutes: int = Field(ge=0)
    daily_periods: list[DailyPlanningPeriod]

    @field_validator("timezone")
    @classmethod
    def valid_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)  # check if the timezone is valid
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError("Timezone must be a valid IANA timezone") from None
        return value

    @field_validator("window_start", "window_end")
    @classmethod
    def timezone_aware(cls, value: datetime) -> datetime:
        return _require_timezone_aware(
            value
        )  # ensure that the timestamps are timezone-aware

    @model_validator(mode="after")
    def valid_constraints(self):
        if self.window_end <= self.window_start:
            raise ValueError("Window end must be later than window start")

        user_timezone = ZoneInfo(self.timezone)  # use the validated timezone
        seen_dates: set[date] = set()  # track dates that have already been seen

        for period in self.daily_periods:
            if period.date in seen_dates:  # check if the date has already been seen
                raise ValueError("Daily planning-period dates must be unique")
            seen_dates.add(period.date)  # if not, add it

            if (
                period.start_at < self.window_start or period.end_at > self.window_end
            ):  # check if the daily period is within the planning window
                raise ValueError(
                    "Daily planning periods must be inside the planning window"
                )

            # Check if the daily period's date matches its local timestamps.
            local_start_date = period.start_at.astimezone(user_timezone).date()
            local_end_date = period.end_at.astimezone(user_timezone).date()
            if local_start_date != period.date or local_end_date != period.date:
                raise ValueError(
                    "Daily planning-period date must match its local timestamps"
                )

        return self
