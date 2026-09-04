"""Pydantic schemas for study schedules proposed before API persistence."""

from typing import Literal

from pydantic import Field, model_validator

from .base import ToolInputModel
from .study_session import SessionStatus, StudySessionCreate
from .study_task import StudyTaskCreate, TaskStatus


_DRAFT_KEY_PATTERN = r"^[a-z0-9]+(?:_[a-z0-9]+)*$"


class DraftTask(StudyTaskCreate):
    """A proposed task identified by a temporary key until it is persisted."""

    draft_task_id: str = Field(
        min_length=1,
        pattern=_DRAFT_KEY_PATTERN,
        description=(
            "Unique temporary snake_case key derived from the task name, such as "
            "'database_exam'. Keep this key stable during validation and revision."
        ),
    )
    task_status: Literal[TaskStatus.TODO] = Field(
        default=TaskStatus.TODO,
        description="Draft tasks must start in the todo state.",
    )


class DraftStudySession(StudySessionCreate):
    """A proposed session linked to a draft task by its temporary key."""

    draft_session_id: str = Field(
        min_length=1,
        pattern=_DRAFT_KEY_PATTERN,
        description=(
            "Unique temporary key using the format "
            "'<draft_task_id>_session_<number>', such as "
            "'database_exam_session_1'."
        ),
    )
    draft_task_id: str = Field(
        min_length=1,
        pattern=_DRAFT_KEY_PATTERN,
        description=(
            "Temporary task reference, such as 'database_exam'. It must exactly "
            "match the associated DraftTask.draft_task_id."
        ),
    )
    task_id: None = Field(
        default=None,
        description=(
            "Real API task ID. It remains null in a draft and is replaced with the "
            "persisted task ID when constructing StudySessionCreate."
        ),
    )
    status: Literal[SessionStatus.SCHEDULED] = Field(
        default=SessionStatus.SCHEDULED,
        description="Draft study sessions must start in the scheduled state.",
    )


class Draft(ToolInputModel):
    """One proposed task together with the sessions that work toward it."""

    task: DraftTask
    study_sessions: list[DraftStudySession] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_session_links(self):
        session_ids: set[str] = set()

        for session in self.study_sessions:
            if session.draft_session_id in session_ids: # checks for dups
                raise ValueError("Draft session IDs must be unique within a draft")
            session_ids.add(session.draft_session_id) #else add them 

            expected_prefix = f"{self.task.draft_task_id}_session_"
            session_number = session.draft_session_id.removeprefix(expected_prefix)
            if (
                not session.draft_session_id.startswith(expected_prefix)
                or not session_number.isdigit()
                or int(session_number) < 1
            ): # checks if it doesn't start with prefix  or session_number is not a digit or session_number is less than 1
                raise ValueError(
                    "Each draft_session_id must use the format "
                    "'<draft_task_id>_session_<number>'"
                )

            if session.draft_task_id != self.task.draft_task_id: # checks if the draft_task_id of the session matches the draft_task_id of the task
                raise ValueError(
                    "Each session draft_task_id must match its draft task"
                )

            if session.subject_id != self.task.subject: # checks if the subject_id of the session matches the subject of the task
                raise ValueError("Task and session subjects must match")

        return self


class DraftSchedule(ToolInputModel):
    """A complete proposed schedule containing one or more task drafts."""
    drafts: list[Draft] = Field(min_length=1)

    @model_validator(mode="after")
    def require_unique_draft_ids(self):
        # checks that all draft task IDs are unique within the schedule
        task_ids: set[str] = set()
        session_ids: set[str] = set()

        for draft in self.drafts: # foreach draft in the list of drafts
            task_id = draft.task.draft_task_id 
            if task_id in task_ids: #check if task_id is already in the set of task_ids
                raise ValueError("Draft task IDs must be unique within a schedule")
            task_ids.add(task_id)

            for session in draft.study_sessions:
                if session.draft_session_id in session_ids: #check if session_id is already in the set of session_ids
                    raise ValueError(
                        "Draft session IDs must be unique within a schedule"
                    )
                session_ids.add(session.draft_session_id)

        return self
