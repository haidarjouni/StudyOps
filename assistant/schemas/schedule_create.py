"""Schemas for persisting an approved draft schedule through the API."""

from pydantic import BaseModel, Field

from .study_session import StudySession, StudySessionCreate
from .study_task import StudyTask, StudyTaskCreate


class ScheduleItemCreate(BaseModel):
    task: StudyTaskCreate
    sessions: list[StudySessionCreate] = Field(min_length=1)


class ScheduleCreate(BaseModel):
    drafts: list[ScheduleItemCreate] = Field(min_length=1)


class CreatedScheduleItem(BaseModel):
    task: StudyTask
    sessions: list[StudySession]


class ScheduleResponse(BaseModel):
    drafts: list[CreatedScheduleItem]
