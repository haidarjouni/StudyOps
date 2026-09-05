
from typing import Literal

from pydantic import Field

from .base import ToolInputModel


class ValidationNote(ToolInputModel):
    code: Literal[
        "outside_planning_window",
        "outside_available_period",
        "period_extension",
        "overlap",
        "insufficient_buffer",
        "estimated_minutes_exceeded",
    ]
    message: str = Field(min_length=1)
    draft_task_id: str | None = None
    draft_session_id: str | None = None
    related_session_id: str | None = None
