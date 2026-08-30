from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

import tools
from context import RequestContext
from schemas import StudyPreference, StudySession, StudyTask, Subject
from tools import (
    GetSessionsInput,
    GetTasksInput,
    get_preferences,
    get_sessions,
    get_tasks,
    list_subjects,
)


def make_task(
    *,
    task_id: int,
    status: str,
    due_date: str,
) -> StudyTask:
    return StudyTask.model_validate(
        {
            "id": task_id,
            "user": 10,
            "subject": 2,
            "title": f"Task {task_id}",
            "description": "Complete the assigned work.",
            "task_type": "study",
            "task_status": status,
            "task_priority": "medium",
            "estimated_minutes": 60,
            "due_date": due_date,
            "created_at": "2026-08-29T10:00:00Z",
            "updated_at": "2026-08-29T10:00:00Z",
        }
    )


def make_session(
    *,
    session_id: int,
    start_at: str,
    end_at: str,
) -> StudySession:
    return StudySession.model_validate(
        {
            "id": session_id,
            "user": 10,
            "subject": {
                "id": 2,
                "user": 10,
                "name": "Computer Science",
                "code": "CS101",
                "semester": 1,
                "created_at": "2026-08-20T09:00:00Z",
                "updated_at": "2026-08-20T09:00:00Z",
            },
            "task": {
                "id": 3,
                "user": 10,
                "subject": 2,
                "title": "Review graph algorithms",
                "description": "Review BFS and DFS.",
                "task_type": "study",
                "task_status": "in_progress",
                "task_priority": "high",
                "estimated_minutes": 60,
                "due_date": "2026-09-05T18:00:00Z",
                "created_at": "2026-08-25T10:00:00Z",
                "updated_at": "2026-08-27T14:30:00Z",
            },
            "start_at": start_at,
            "end_at": end_at,
            "status": "scheduled",
            "created_at": "2026-08-28T09:30:00Z",
            "updated_at": "2026-08-28T09:30:00Z",
        }
    )


def make_subject(
    *,
    subject_id: int,
    name: str,
    code: str,
    semester: int,
) -> Subject:
    return Subject.model_validate(
        {
            "id": subject_id,
            "user": 10,
            "name": name,
            "code": code,
            "semester": semester,
            "created_at": "2026-08-20T09:00:00Z",
            "updated_at": "2026-08-20T09:00:00Z",
        }
    )


@pytest.mark.asyncio
async def test_get_tasks_fetches_active_tasks_and_returns_compact_sorted_json(
    monkeypatch,
):
    calls = []

    class FakeClient:
        def __init__(
            self,
            base_url,
            *,
            access_token=None,
            refresh_token=None,
        ):
            assert base_url
            assert access_token == "access-token"
            assert refresh_token == "refresh-token"

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def list_study_tasks(self, **filters):
            calls.append(filters)
            if filters["task_status"] == "todo":
                return [
                    make_task(
                        task_id=2,
                        status="todo",
                        due_date="2026-09-05T12:00:00Z",
                    )
                ]
            return [
                make_task(
                    task_id=1,
                    status="in_progress",
                    due_date="2026-09-01T12:00:00Z",
                )
            ]

    monkeypatch.setattr(tools, "StudyOpsAPIClient", FakeClient)
    runtime = SimpleNamespace(
        context=RequestContext(
            access_token="access-token",
            refresh_token="refresh-token",
        )
    )
    due_before = datetime(2026, 9, 7, 23, 59, tzinfo=timezone.utc)

    result = await get_tasks.coroutine(
        runtime=runtime,
        subject=2,
        due_before=due_before,
    )

    assert [task["id"] for task in result] == [1, 2]
    assert "user" not in result[0]
    assert "created_at" not in result[0]
    assert calls == [
        {
            "task_status": "todo",
            "subject": 2,
            "due_to": "2026-09-07T23:59:00+00:00",
        },
        {
            "task_status": "in_progress",
            "subject": 2,
            "due_to": "2026-09-07T23:59:00+00:00",
        },
    ]


def test_get_tasks_schema_rejects_a_naive_deadline():
    with pytest.raises(ValidationError, match="due_before must include a timezone"):
        GetTasksInput(due_before=datetime(2026, 9, 7, 23, 59))


def test_runtime_context_is_hidden_from_the_model_schema():
    properties = get_tasks.tool_call_schema.model_json_schema()["properties"]

    assert set(properties) == {"subject", "due_before"}


@pytest.mark.asyncio
async def test_get_preferences_returns_json_compatible_preferences(monkeypatch):
    calls = 0

    class FakeClient:
        def __init__(
            self,
            base_url,
            *,
            access_token=None,
            refresh_token=None,
        ):
            assert base_url
            assert access_token == "access-token"
            assert refresh_token == "refresh-token"

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def get_preferences(self):
            nonlocal calls
            calls += 1
            return StudyPreference.model_validate(
                {
                    "timezone": "Asia/Beirut",
                    "earliest_study_time": "08:00:00",
                    "latest_study_time": "22:00:00",
                    "preferred_session_minutes": 45,
                    "buffer_minutes": 10,
                }
            )

    monkeypatch.setattr(tools, "StudyOpsAPIClient", FakeClient)
    runtime = SimpleNamespace(
        context=RequestContext(
            access_token="access-token",
            refresh_token="refresh-token",
        )
    )

    result = await get_preferences.coroutine(runtime=runtime)

    assert calls == 1
    assert result == {
        "timezone": "Asia/Beirut",
        "earliest_study_time": "08:00:00",
        "latest_study_time": "22:00:00",
        "preferred_session_minutes": 45,
        "buffer_minutes": 10,
    }


def test_get_preferences_has_no_model_supplied_arguments():
    properties = get_preferences.tool_call_schema.model_json_schema()["properties"]

    assert properties == {}


@pytest.mark.asyncio
async def test_get_sessions_uses_overlap_filters_and_returns_sorted_compact_json(
    monkeypatch,
):
    calls = []

    class FakeClient:
        def __init__(
            self,
            base_url,
            *,
            access_token=None,
            refresh_token=None,
        ):
            assert base_url
            assert access_token == "access-token"
            assert refresh_token == "refresh-token"

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def list_sessions(self, **filters):
            calls.append(filters)
            return [
                make_session(
                    session_id=2,
                    start_at="2026-09-02T12:00:00Z",
                    end_at="2026-09-02T13:00:00Z",
                ),
                make_session(
                    session_id=1,
                    start_at="2026-09-01T12:00:00Z",
                    end_at="2026-09-01T13:00:00Z",
                ),
            ]

    monkeypatch.setattr(tools, "StudyOpsAPIClient", FakeClient)
    runtime = SimpleNamespace(
        context=RequestContext(
            access_token="access-token",
            refresh_token="refresh-token",
        )
    )
    window_start = datetime(2026, 9, 1, tzinfo=timezone.utc)
    window_end = datetime(2026, 9, 8, tzinfo=timezone.utc)

    result = await get_sessions.coroutine(
        runtime=runtime,
        window_start=window_start,
        window_end=window_end,
        subject=2,
    )

    assert calls == [
        {
            "status": "scheduled",
            "subject": 2,
            "window_start": "2026-09-01T00:00:00+00:00",
            "window_end": "2026-09-08T00:00:00+00:00",
        }
    ]
    assert [session["id"] for session in result] == [1, 2]
    assert result[0]["subject"] == {
        "id": 2,
        "name": "Computer Science",
        "code": "CS101",
    }
    assert result[0]["task"] == {
        "id": 3,
        "title": "Review graph algorithms",
    }
    assert "user" not in result[0]


@pytest.mark.parametrize(
    ("window_start", "window_end", "message"),
    [
        (
            datetime(2026, 9, 1),
            datetime(2026, 9, 2, tzinfo=timezone.utc),
            "must include a timezone",
        ),
        (
            datetime(2026, 9, 2, tzinfo=timezone.utc),
            datetime(2026, 9, 1, tzinfo=timezone.utc),
            "must be later than",
        ),
        (
            datetime(2026, 9, 1, tzinfo=timezone.utc),
            datetime(2026, 10, 2, tzinfo=timezone.utc),
            "cannot be longer than 30 days",
        ),
    ],
)
def test_get_sessions_rejects_invalid_windows(
    window_start,
    window_end,
    message,
):
    with pytest.raises(ValidationError, match=message):
        GetSessionsInput(
            window_start=window_start,
            window_end=window_end,
        )


def test_get_sessions_public_schema_hides_runtime_context():
    properties = get_sessions.tool_call_schema.model_json_schema()["properties"]

    assert set(properties) == {"window_start", "window_end", "subject"}


@pytest.mark.asyncio
async def test_list_subjects_returns_sorted_compact_json(monkeypatch):
    calls = 0

    class FakeClient:
        def __init__(
            self,
            base_url,
            *,
            access_token=None,
            refresh_token=None,
        ):
            assert base_url
            assert access_token == "access-token"
            assert refresh_token == "refresh-token"

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return None

        async def list_subjects(self):
            nonlocal calls
            calls += 1
            return [
                make_subject(
                    subject_id=2,
                    name="Physics",
                    code="PHYS101",
                    semester=1,
                ),
                make_subject(
                    subject_id=1,
                    name="Computer Science",
                    code="CS101",
                    semester=2,
                ),
            ]

    monkeypatch.setattr(tools, "StudyOpsAPIClient", FakeClient)
    runtime = SimpleNamespace(
        context=RequestContext(
            access_token="access-token",
            refresh_token="refresh-token",
        )
    )

    result = await list_subjects.coroutine(runtime=runtime)

    assert calls == 1
    assert result == [
        {
            "id": 1,
            "name": "Computer Science",
            "code": "CS101",
            "semester": 2,
        },
        {
            "id": 2,
            "name": "Physics",
            "code": "PHYS101",
            "semester": 1,
        },
    ]


def test_list_subjects_has_no_model_supplied_arguments():
    properties = list_subjects.tool_call_schema.model_json_schema()["properties"]

    assert properties == {}
