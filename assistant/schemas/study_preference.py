"""Pydantic schemas for study-preference API operations."""

from datetime import time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import Field, field_validator, model_validator

from .base import APIResponseModel, ToolInputModel


def _validate_timezone(value: str) -> str:
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown IANA timezone: {value}") from exc
    return value


def _validate_clock_time(value: time) -> time:
    if value.tzinfo is not None and value.utcoffset() is not None:
        raise ValueError(
            "study-window times must not contain an offset; use the timezone field"
        )
    return value


class StudyPreference(APIResponseModel):
    """A user's scheduling preferences returned by the StudyOps API."""

    timezone: str = Field(
        min_length=1,
        max_length=64,
        description="IANA timezone used to interpret the user's local schedule.",
    )
    earliest_study_time: time = Field(
        description="Earliest local wall-clock time at which study may begin."
    )
    latest_study_time: time = Field(
        description="Latest local wall-clock time at which study may occur."
    )
    preferred_session_minutes: int = Field(
        gt=0,
        description="Preferred duration of an individual study session, in minutes.",
    )
    buffer_minutes: int = Field(
        ge=0,
        description="Minimum break or transition time between sessions, in minutes.",
    )

    _timezone_exists = field_validator("timezone")(_validate_timezone)
    _times_are_local = field_validator("earliest_study_time", "latest_study_time")(
        _validate_clock_time
    )

    @model_validator(mode="after")
    def require_valid_study_window(self):
        if self.earliest_study_time >= self.latest_study_time:
            raise ValueError("latest_study_time must be later than earliest_study_time")
        return self


class StudyPreferenceCreate(ToolInputModel):
    """Values accepted when creating initial study preferences."""

    timezone: str = Field(
        default="UTC",
        min_length=1,
        max_length=64,
        description=(
            "User's IANA timezone, such as Asia/Beirut. Use UTC only when it is "
            "actually the user's intended timezone."
        ),
    )
    earliest_study_time: time = Field(
        description="Earliest preferred local study time."
    )
    latest_study_time: time = Field(
        description="Latest preferred local study time; must be later than earliest."
    )
    preferred_session_minutes: int = Field(
        gt=0,
        description="Preferred study-session duration in minutes.",
    )
    buffer_minutes: int = Field(
        ge=0,
        description="Desired non-negative break between sessions, in minutes.",
    )

    _timezone_exists = field_validator("timezone")(_validate_timezone)
    _times_are_local = field_validator("earliest_study_time", "latest_study_time")(
        _validate_clock_time
    )

    @model_validator(mode="after")
    def require_valid_study_window(self):
        if self.earliest_study_time >= self.latest_study_time:
            raise ValueError("latest_study_time must be later than earliest_study_time")
        return self


class StudyPreferenceUpdate(ToolInputModel):
    """Fields that may be changed with a partial preference update."""

    timezone: str | None = Field(
        default=None,
        min_length=1,
        max_length=64,
        description="New IANA timezone for interpreting the user's local schedule.",
    )
    earliest_study_time: time | None = Field(
        default=None,
        description="New earliest preferred local study time.",
    )
    latest_study_time: time | None = Field(
        default=None,
        description="New latest preferred local study time.",
    )
    preferred_session_minutes: int | None = Field(
        default=None,
        gt=0,
        description="New preferred session duration in minutes.",
    )
    buffer_minutes: int | None = Field(
        default=None,
        ge=0,
        description="New non-negative break between sessions, in minutes.",
    )

    @field_validator("timezone")
    @classmethod
    def timezone_exists(cls, value: str | None) -> str | None:
        return _validate_timezone(value) if value is not None else None

    @field_validator("earliest_study_time", "latest_study_time")
    @classmethod
    def times_are_local(cls, value: time | None) -> time | None:
        return _validate_clock_time(value) if value is not None else None

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_dump(exclude_none=True):
            raise ValueError("At least one non-null field must be supplied")

        if (
            self.earliest_study_time is not None
            and self.latest_study_time is not None
            and self.earliest_study_time >= self.latest_study_time
        ):
            raise ValueError("latest_study_time must be later than earliest_study_time")

        return self
