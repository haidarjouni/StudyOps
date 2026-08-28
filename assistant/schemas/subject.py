"""Pydantic schemas for subject API operations."""

from datetime import datetime

from pydantic import Field, field_validator, model_validator

from .base import APIResponseModel, ToolInputModel


class Subject(APIResponseModel):
    """A subject returned by the StudyOps API."""

    id: int = Field(gt=0, description="Unique identifier of the subject.")
    user: int = Field(gt=0, description="Identifier of the user who owns the subject.")
    name: str = Field(
        min_length=1,
        max_length=100,
        description="Human-readable subject name, such as Calculus II.",
    )
    code: str = Field(
        min_length=1,
        max_length=10,
        description="Short uppercase subject code, such as MATH201.",
    )
    semester: int = Field(
        gt=0,
        description="Positive semester number associated with the subject.",
    )
    created_at: datetime = Field(description="Timestamp when the subject was created.")
    updated_at: datetime = Field(
        description="Timestamp when the subject was last updated."
    )


class SubjectCreate(ToolInputModel):
    """Values accepted when creating a subject."""

    name: str = Field(
        min_length=1,
        max_length=100,
        description="Human-readable subject name. Do not invent it if unclear.",
    )
    code: str = Field(
        min_length=1,
        max_length=10,
        description=(
            "Short subject code. It is normalized to uppercase and must be unique "
            "among the user's subjects."
        ),
    )
    semester: int = Field(
        gt=0,
        description="Positive semester number for the subject.",
    )

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.upper()


class SubjectUpdate(ToolInputModel):
    """Fields that may be changed with a partial subject update."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="New human-readable subject name.",
    )
    code: str | None = Field(
        default=None,
        min_length=1,
        max_length=10,
        description="New unique subject code; normalized to uppercase.",
    )
    semester: int | None = Field(
        default=None,
        gt=0,
        description="New positive semester number.",
    )

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str | None) -> str | None:
        return value.upper() if value is not None else None

    @model_validator(mode="after")
    def require_at_least_one_change(self):
        if not self.model_dump(exclude_none=True):
            raise ValueError("At least one non-null field must be supplied")
        return self


class SubjectDelete(ToolInputModel):
    """Arguments required to delete a subject."""

    subject_id: int = Field(
        gt=0,
        description=(
            "Identifier of the subject to delete. Deleting a subject may also delete "
            "its tasks and sessions, so explicit user confirmation is required."
        ),
    )
