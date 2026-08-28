"""Pydantic schemas for study-task API operations."""

from datetime import datetime
from enum import Enum

from pydantic import Field, field_validator, model_validator

from .base import APIResponseModel, ToolInputModel


class TaskType(str, Enum):
    ASSIGNMENT = "assignment"
    EXAM = "exam"
    STUDY = "study"
    OTHER = "other"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class StudyTask(APIResponseModel):
    """A study task returned by the StudyOps API."""

    id: int = Field(gt=0, description="Unique identifier of the study task.")
    user: int = Field(gt=0, description="Identifier of the user who owns the task.")
    subject: int = Field(
        gt=0,
        description="Identifier of the subject this task belongs to.",
    )
    title: str = Field(
        min_length=1,
        max_length=100,
        description="Short, specific name of the task.",
    )
    description: str = Field(
        min_length=1,
        description="Detailed instructions or context for completing the task.",
    )
    task_type: TaskType = Field(
        description=(
            "Category: assignment for coursework, exam for assessment preparation, "
            "study for general study, or other when none applies."
        )
    )
    task_status: TaskStatus = Field(
        description="Progress state: todo, in_progress, done, or cancelled."
    )
    task_priority: TaskPriority = Field(
        description="Importance of the task: low, medium, or high."
    )
    estimated_minutes: int = Field(
        gt=0,
        description="Estimated duration required to finish the task, in minutes.",
    )
    due_date: datetime = Field(description="Timezone-aware deadline for the task.")
    created_at: datetime = Field(description="Timestamp when the task was created.")
    updated_at: datetime = Field(
        description="Timestamp when the task was last updated."
    )

    @field_validator("due_date")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("due_date must include a timezone")
        return value


class StudyTaskCreate(ToolInputModel):
    """Values accepted when creating a study task."""

    subject: int = Field(
        gt=0,
        description="Identifier of the subject this task belongs to.",
    )
    title: str = Field(
        min_length=1,
        max_length=100,
        description="Short, specific name for the task.",
    )
    description: str = Field(
        min_length=1,
        description=(
            "Details about what the student needs to do. This field is required by "
            "the API; ask for clarification rather than inventing important details."
        ),
    )
    task_type: TaskType = Field(
        default=TaskType.OTHER,
        description=(
            "Category: assignment for coursework, exam for assessment preparation, "
            "study for general study, or other when none applies."
        ),
    )
    task_status: TaskStatus = Field(
        default=TaskStatus.TODO,
        description=(
            "Initial progress state: todo, in_progress, done, or cancelled. New "
            "tasks normally start as todo."
        ),
    )
    task_priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Importance of the task: low, medium, or high.",
    )
    estimated_minutes: int = Field(
        gt=0,
        description="Estimated duration in minutes.",
    )
    due_date: datetime = Field(
        description=(
            "Timezone-aware deadline. Do not guess this value; ask the user "
            "when the deadline cannot be determined."
        ),
    )

    @field_validator("due_date")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("due_date must include a timezone")
        return value


class StudyTaskUpdate(ToolInputModel):
    """Fields that may be changed with a partial task update."""

    subject: int | None = Field(
        default=None,
        gt=0,
        description="Identifier of the new subject for this task.",
    )
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="New short, specific title for the task.",
    )
    description: str | None = Field(
        default=None,
        min_length=1,
        description="New task details or completion instructions.",
    )
    task_type: TaskType | None = Field(
        default=None,
        description="New category: assignment, exam, study, or other.",
    )
    task_status: TaskStatus | None = Field(
        default=None,
        description="New progress state: todo, in_progress, done, or cancelled.",
    )
    task_priority: TaskPriority | None = Field(
        default=None,
        description="New importance level: low, medium, or high.",
    )
    estimated_minutes: int | None = Field(
        default=None,
        gt=0,
        description="New estimated duration in minutes.",
    )
    due_date: datetime | None = Field(
        default=None,
        description="New timezone-aware deadline for the task.",
    )

    @field_validator("due_date")
    @classmethod
    def require_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None:
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError("due_date must include a timezone")
        return value

    @model_validator(mode="after")
    def require_at_least_one_change(self):
        if not self.model_dump(exclude_none=True):
            raise ValueError("At least one non-null field must be supplied")
        return self


class StudyTaskDelete(ToolInputModel):
    """Arguments required to delete a study task."""

    task_id: int = Field(
        gt=0,
        description=(
            "Identifier of the study task to delete. The assistant must obtain "
            "explicit user confirmation before deletion."
        ),
    )
