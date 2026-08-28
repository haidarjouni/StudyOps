"""Pydantic schemas for study-session API operations."""

from datetime import datetime
from enum import Enum

from pydantic import Field, field_validator, model_validator

from .base import APIResponseModel, ToolInputModel
from .study_task import StudyTask
from .subject import Subject


class SessionStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class StudySession(APIResponseModel):
    """A scheduled study session returned by the StudyOps API."""

    id: int = Field(gt=0, description="Unique identifier of the study session.")
    user: int = Field(
        gt=0,
        description="Identifier of the user who owns the study session.",
    )
    subject: Subject = Field(description="Subject scheduled for this session.")
    task: StudyTask | None = Field(
        default=None,
        description="Optional task planned for this session.",
    )
    start_at: datetime = Field(
        description="Timezone-aware timestamp when the session starts."
    )
    end_at: datetime = Field(
        description="Timezone-aware timestamp when the session ends."
    )
    status: SessionStatus = Field(
        description="Current session state: scheduled, completed, or cancelled."
    )
    created_at: datetime = Field(description="Timestamp when the session was created.")
    updated_at: datetime = Field(
        description="Timestamp when the session was last updated."
    )

    @field_validator("start_at", "end_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("session timestamps must include a timezone")
        return value

    @model_validator(mode="after")
    def require_valid_time_range(self):
        if self.start_at >= self.end_at:
            raise ValueError("end_at must be later than start_at")
        if self.task is not None and self.task.subject != self.subject.id:
            raise ValueError("task and session subject must match")
        return self


class StudySessionCreate(ToolInputModel):
    """Values accepted when scheduling a study session."""

    subject_id: int = Field(
        gt=0,
        description="Identifier of the subject to study during this session.",
    )
    task_id: int | None = Field(
        default=None,
        gt=0,
        description=(
            "Optional task to work on. It must belong to the selected subject and "
            "must not already be completed or cancelled."
        ),
    )
    start_at: datetime = Field(
        description=(
            "Timezone-aware session start. Resolve relative times using the user's "
            "configured timezone and do not guess an ambiguous date or time."
        )
    )
    end_at: datetime = Field(
        description="Timezone-aware session end; it must be later than start_at."
    )
    status: SessionStatus = Field(
        default=SessionStatus.SCHEDULED,
        description=(
            "Initial state: scheduled, completed, or cancelled. New sessions normally "
            "start as scheduled."
        ),
    )

    @field_validator("start_at", "end_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("session timestamps must include a timezone")
        return value

    @model_validator(mode="after")
    def require_valid_time_range(self):
        if self.start_at >= self.end_at:
            raise ValueError("end_at must be later than start_at")
        return self


class StudySessionUpdate(ToolInputModel):
    """Fields that may be changed with a partial session update."""

    subject_id: int | None = Field(
        default=None,
        gt=0,
        description="Identifier of the new subject for this session.",
    )
    task_id: int | None = Field(
        default=None,
        gt=0,
        description=(
            "Identifier of the new task. An explicit null value removes the task "
            "from the session."
        ),
    )
    start_at: datetime | None = Field(
        default=None,
        description="New timezone-aware start timestamp.",
    )
    end_at: datetime | None = Field(
        default=None,
        description="New timezone-aware end timestamp.",
    )
    status: SessionStatus | None = Field(
        default=None,
        description="New session state: scheduled, completed, or cancelled.",
    )

    @field_validator("start_at", "end_at")
    @classmethod
    def require_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None:
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError("session timestamps must include a timezone")
        return value

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be supplied")

        non_nullable_fields = {"subject_id", "start_at", "end_at", "status"}
        null_fields = [
            name
            for name in non_nullable_fields
            if name in self.model_fields_set and getattr(self, name) is None
        ]
        if null_fields:
            raise ValueError(f"These fields cannot be null: {', '.join(null_fields)}")

        if (
            self.start_at is not None
            and self.end_at is not None
            and self.start_at >= self.end_at
        ):
            raise ValueError("end_at must be later than start_at")

        return self


class StudySessionDelete(ToolInputModel):
    """Arguments required to delete a study session."""

    session_id: int = Field(
        gt=0,
        description=(
            "Identifier of the study session to delete. The assistant must obtain "
            "explicit user confirmation before deletion."
        ),
    )
