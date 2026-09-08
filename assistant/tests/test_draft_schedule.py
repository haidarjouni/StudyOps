from datetime import datetime

import pytest
from pydantic import ValidationError

from schemas import (Draft, DraftSchedule, DraftStudySession, DraftTask,
                     StudySessionCreate, StudyTaskCreate)


def make_task(**changes) -> DraftTask:
    values = {
        "draft_task_id": "database_exam",
        "subject": 4,
        "title": "Prepare for database exam",
        "description": "Review all database exam topics.",
        "task_type": "exam",
        "task_priority": "high",
        "estimated_minutes": 180,
        "due_date": datetime.fromisoformat("2026-09-11T09:00:00+03:00"),
    }
    values.update(changes)
    return DraftTask(**values)


def make_session(**changes) -> DraftStudySession:
    values = {
        "draft_session_id": "database_exam_session_1",
        "draft_task_id": "database_exam",
        "subject_id": 4,
        "start_at": datetime.fromisoformat("2026-09-05T16:00:00+03:00"),
        "end_at": datetime.fromisoformat("2026-09-05T17:00:00+03:00"),
    }
    values.update(changes)
    return DraftStudySession(**values)


def test_draft_schedule_links_sessions_to_task():
    schedule = DraftSchedule(
        drafts=[Draft(task=make_task(), study_sessions=[make_session()])]
    )

    assert schedule.drafts[0].study_sessions[0].task_id is None
    assert schedule.drafts[0].study_sessions[0].draft_task_id == "database_exam"


def test_drafts_convert_to_create_schemas_after_task_persistence():
    draft_task = make_task()
    draft_session = make_session()

    task_payload = StudyTaskCreate.model_validate(
        draft_task.model_dump(exclude={"draft_task_id"})
    )
    session_values = draft_session.model_dump(
        exclude={"draft_session_id", "draft_task_id", "task_id"}
    )
    session_values["task_id"] = 42
    session_payload = StudySessionCreate.model_validate(session_values)

    assert task_payload.subject == 4
    assert session_payload.task_id == 42


def test_draft_rejects_session_for_a_different_task():
    with pytest.raises(ValidationError, match="draft_task_id must match"):
        Draft(
            task=make_task(),
            study_sessions=[make_session(draft_task_id="other_task")],
        )


def test_draft_rejects_session_for_a_different_subject():
    with pytest.raises(ValidationError, match="subjects must match"):
        Draft(task=make_task(), study_sessions=[make_session(subject_id=7)])


def test_draft_rejects_session_id_with_the_wrong_task_prefix():
    with pytest.raises(ValidationError, match="draft_session_id must use the format"):
        Draft(
            task=make_task(),
            study_sessions=[make_session(draft_session_id="other_task_session_1")],
        )


def test_draft_rejects_non_numeric_session_number():
    with pytest.raises(ValidationError, match="draft_session_id must use the format"):
        Draft(
            task=make_task(),
            study_sessions=[make_session(draft_session_id="database_exam_session_one")],
        )
