"""LangChain tools exposed to the StudyOps assistant."""

from datetime import datetime, timedelta
from typing import Any

from langchain.tools import ToolRuntime, tool
from pydantic import Field, field_validator, model_validator

from api_client import StudyOpsAPIClient
from config import Config
from context import RequestContext
from schemas import SessionStatus, StudySession, StudyTask, Subject, TaskStatus
from schemas.base import ToolInputModel


class GetSessionsInput(ToolInputModel):
    """Filters the model may choose when gathering scheduled sessions."""

    window_start: datetime = Field(
        description=(
            "Start of the planning window as a timezone-aware timestamp. "
            "Sessions continuing into the window are included."
        ),
    )
    window_end: datetime = Field(
        description=(
            "End of the planning window as a timezone-aware timestamp. "
            "Sessions beginning before this boundary are included."
        ),
    )
    subject: int | None = Field(
        default=None,
        gt=0,
        description="Only return sessions belonging to this subject ID.",
    )

    @field_validator("window_start", "window_end")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("session window timestamps must include a timezone")
        return value

    @model_validator(mode="after")
    def check_window(self):
        if self.window_start >= self.window_end:
            raise ValueError("window_end must be later than window_start")
        if self.window_end - self.window_start > timedelta(days=30):
            raise ValueError("session window cannot be longer than 30 days")
        return self


class GetTasksInput(ToolInputModel):
    """Filters the model may choose when gathering tasks for a study plan."""

    subject: int | None = Field(
        default=None,
        gt=0,
        description="Only return active tasks belonging to this subject ID.",
    )
    due_before: datetime | None = Field(
        default=None,
        description=(
            "Latest deadline to include, as a timezone-aware timestamp. "
            "Leave empty when every active task is needed."
        ),
    )

    @field_validator("due_before")
    @classmethod
    def require_timezone(cls, value: datetime | None) -> datetime | None:
        if value is not None and (
            value.tzinfo is None or value.utcoffset() is None
        ):
            raise ValueError("due_before must include a timezone")
        return value


def _task_for_model(task: StudyTask) -> dict[str, Any]:
    """Remove response metadata that does not help the model plan."""

    return task.model_dump(
        mode="json",
        exclude={"user", "created_at", "updated_at"},
)


def _session_for_model(session: StudySession) -> dict[str, Any]:
    """Return only the session details needed for planning."""

    task = session.task
    return {
        "id": session.id,
        "subject": {
            "id": session.subject.id,
            "name": session.subject.name,
            "code": session.subject.code,
        },
        "task": (
            None
            if task is None
            else {
                "id": task.id,
                "title": task.title,
            }
        ),
        "start_at": session.start_at.isoformat(),
        "end_at": session.end_at.isoformat(),
        "status": session.status.value,
    }


@tool(args_schema=GetTasksInput)
async def get_tasks(
    runtime: ToolRuntime[RequestContext],
    subject: int | None = None,
    due_before: datetime | None = None,
) -> list[dict[str, Any]]:
    """Get the current user's unfinished tasks for study planning.

    Returns both todo and in-progress tasks, including overdue tasks. Use
    due_before to limit the result to deadlines within a planning horizon.
    This tool only reads data; it never creates or changes a task.
    """

    due_to = due_before.isoformat() if due_before is not None else None
    settings = Config()

    async with StudyOpsAPIClient(
        settings.base_drf_api,
        access_token=runtime.context.access_token,
        refresh_token=runtime.context.refresh_token,
    ) as client:
        tasks: list[StudyTask] = []

        for status in (TaskStatus.TODO, TaskStatus.IN_PROGRESS):
            tasks.extend(
                await client.list_study_tasks(
                    task_status=status.value,
                    subject=subject,
                    due_to=due_to,
                )
            )

    tasks.sort(key=lambda task: (task.due_date, task.id))
    return [_task_for_model(task) for task in tasks]


@tool
async def get_preferences(runtime: ToolRuntime[RequestContext]) -> dict[str, Any]:
    """Get the current user's preferences for study planning.

    Returns a dictionary of preference names and values. This tool only reads
    data; it never creates or changes a preference.
    """

    settings = Config()

    async with StudyOpsAPIClient(
        settings.base_drf_api,
        access_token=runtime.context.access_token,
        refresh_token=runtime.context.refresh_token,
    ) as client:
        preferences = await client.get_preferences()

    return preferences.model_dump(mode="json")


@tool(args_schema=GetSessionsInput)
async def get_sessions(
    runtime: ToolRuntime[RequestContext],
    window_start: datetime,
    window_end: datetime,
    subject: int | None = None,
) -> list[dict[str, Any]]:
    """Get scheduled sessions that overlap a study-planning window.

    Sessions crossing either window boundary are included. Results are ordered
    chronologically. This tool only reads data; it never changes a session.
    """

    settings = Config()

    async with StudyOpsAPIClient(
        settings.base_drf_api,
        access_token=runtime.context.access_token,
        refresh_token=runtime.context.refresh_token,
    ) as client:
        sessions = await client.list_sessions(
            status=SessionStatus.SCHEDULED.value,
            subject=subject,
            window_start=window_start.isoformat(),
            window_end=window_end.isoformat(),
        )

    sessions.sort(key=lambda session: (session.start_at, session.id))

    return [_session_for_model(session) for session in sessions]


def _subject_for_model(subject: Subject) -> dict[str, Any]:
    """Return only the subject details needed for planning."""

    return {
        "id": subject.id,
        "name": subject.name,
        "code": subject.code,
        "semester": subject.semester,
    }


@tool
async def list_subjects(
    runtime: ToolRuntime[RequestContext],
) -> list[dict[str, Any]]:
    """List the current user's subjects for task and session planning."""

    settings = Config()

    async with StudyOpsAPIClient(
        settings.base_drf_api,
        access_token=runtime.context.access_token,
        refresh_token=runtime.context.refresh_token,
    ) as client:
        subjects = await client.list_subjects()

    subjects.sort(key=lambda subject: (subject.name.casefold(), subject.id))
    return [_subject_for_model(subject) for subject in subjects]
