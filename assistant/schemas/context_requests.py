from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class TaskContextRequest(BaseModel):
    source: Literal["tasks"] = Field(description="Request the user's study tasks.")
    reason: str = Field(description="Short explanation of why task data is needed.")
    subject: int | None = Field(
        default=None,
        description=(
            "Subject ID to filter by. Leave null when tasks from all subjects "
            "are relevant or the subject ID is unknown."
        ),
    )
    due_from: datetime = Field(
        description=(
            "Inclusive beginning of the deadline range as a timezone-aware "
            "timestamp. Use the beginning of today in the user's timezone by "
            "default, unless the user requests an earlier or different date."
        ),
    )
    due_before: datetime = Field(
        description=(
            "Inclusive end of the deadline range as a timezone-aware timestamp. "
            "Derive it from the user's request. If no end is specified, use the "
            "end of the day 14 days from today."
        ),
    )

    @field_validator("due_from", "due_before")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("task deadline filters must include a timezone")
        return value

    @model_validator(mode="after")
    def require_valid_due_range(self):
        if self.due_from > self.due_before:
            raise ValueError("due_before must not be earlier than due_from")
        return self


class SessionContextRequest(BaseModel):
    source: Literal["sessions"] = Field(
        description="Request the user's scheduled study sessions."
    )
    reason: str = Field(description="Short explanation of why session data is needed.")
    subject: int | None = Field(
        default=None,
        description=(
            "Subject ID to filter by. Leave null when sessions from all subjects "
            "are relevant or the subject ID is unknown."
        ),
    )
    window_start: datetime = Field(
        description=(
            "Beginning of the requested scheduling window as a timezone-aware "
            "timestamp in the user's timezone. Derive relative dates from the "
            "current date supplied in the system prompt."
        ),
    )
    window_end: datetime = Field(
        description=(
            "Exclusive end of the requested scheduling window as a timezone-aware "
            "timestamp. It must be later than window_start."
        ),
    )

    @field_validator("window_start", "window_end")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("session window timestamps must include a timezone")
        return value

    @model_validator(mode="after")
    def require_valid_window(self):
        if self.window_start >= self.window_end:
            raise ValueError("window_end must be later than window_start")
        return self


class PreferenceContextRequest(BaseModel):
    source: Literal["preferences"] = Field(
        description="Request the user's study preferences."
    )
    reason: str = Field(description="Short explanation of why preferences are needed.")


class SubjectContextRequest(BaseModel):
    source: Literal["subjects"] = Field(description="Request the user's subjects.")
    reason: str = Field(description="Short explanation of why subject data is needed.")


ContextRequest = Annotated[
    TaskContextRequest
    | SessionContextRequest
    | PreferenceContextRequest
    | SubjectContextRequest,
    Field(discriminator="source"),
]
# This annotated type can be any of the four context request types. The
# discriminator field determines which request type is being used.

ContextSource = Literal[
    "tasks",
    "sessions",
    "preferences",
    "subjects",
]


class ContextCheckOutput(BaseModel):
    context_needed: dict[ContextSource, ContextRequest]

    @model_validator(mode="after")
    def require_matching_sources(self):
        for source, request in self.context_needed.items():
            if source != request.source:
                raise ValueError(
                    f"source '{source}' does not match request source '{request.source}'"
                )
        return self
