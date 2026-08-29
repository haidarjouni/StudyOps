import json

import httpx
import pytest

from api_client.client import StudyOpsAPIClient
from api_client.exceptions import APIResponseError
from schemas.study_preference import StudyPreferenceUpdate
from schemas.study_session import StudySessionCreate, StudySessionUpdate
from schemas.subject import SubjectCreate


def session_response_data(
    *,
    start_at: str = "2026-08-28T10:00:00Z",
    end_at: str = "2026-08-28T11:00:00Z",
    status: str = "scheduled",
) -> dict:  # to create responses faster
    return {
        "id": 1,
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
            "title": "Study Sorting Algorithms",
            "description": "Review merge sort and quicksort, then solve practice problems.",
            "task_type": "study",
            "task_status": "in_progress",
            "task_priority": "high",
            "estimated_minutes": 120,
            "due_date": "2026-08-30T18:00:00Z",
            "created_at": "2026-08-25T10:00:00Z",
            "updated_at": "2026-08-27T14:30:00Z",
        },
        "start_at": start_at,
        "end_at": end_at,
        "status": status,
        "created_at": "2026-08-28T09:30:00Z",
        "updated_at": "2026-08-28T09:30:00Z",
    }


def preference_response_data(
    *,
    preferred_session_minutes: int = 45,
    buffer_minutes: int = 10,
) -> dict:
    return {
        "timezone": "Asia/Beirut",
        "earliest_study_time": "08:00:00",
        "latest_study_time": "22:00:00",
        "preferred_session_minutes": preferred_session_minutes,
        "buffer_minutes": buffer_minutes,
    }


@pytest.mark.asyncio
async def test_list_subjects():
    def fake_api(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[
                {
                    "id": 1,
                    "user": 10,
                    "name": "Calculus",
                    "code": "MATH201",
                    "semester": 2,
                    "created_at": "2026-08-28T10:00:00Z",
                    "updated_at": "2026-08-28T10:00:00Z",
                }
            ],
        )

    transport = httpx.MockTransport(fake_api)

    async with StudyOpsAPIClient(
        "http://test/api/",
        transport=transport,
    ) as api:
        subjects = await api.list_subjects()

    assert len(subjects) == 1
    assert subjects[0].name == "Calculus"
    assert subjects[0].code == "MATH201"
    assert subjects[0].semester == 2


@pytest.mark.asyncio
async def test_list_subjects_api_failure():
    def fake_api(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            500,
            json={"detail": "Internal server error"},
        )

    transport = httpx.MockTransport(fake_api)

    async with StudyOpsAPIClient(
        "http://test/api/",
        transport=transport,
    ) as api:
        with pytest.raises(APIResponseError) as error:
            await api.list_subjects()

    assert error.value.status_code == 500


@pytest.mark.asyncio
async def test_create_subject():
    def fake_api(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            201,
            json={
                "id": 2,
                "user": 10,
                "name": "Physics",
                "code": "PHYS101",
                "semester": 1,
                "created_at": "2026-08-28T10:00:00Z",
                "updated_at": "2026-08-28T10:00:00Z",
            },
        )

    transport = httpx.MockTransport(fake_api)
    async with StudyOpsAPIClient(
        "http://test/api/",
        transport=transport,
    ) as api:
        subject = SubjectCreate(
            name="Physics",
            code="phys101",
            semester=1,
        )
        subject2 = await api.create_subject(subject=subject)
    assert subject2.id == 2
    assert subject2.user == 10
    assert subject2.name == "Physics"
    assert subject2.code == "PHYS101"
    assert subject2.semester == 1


@pytest.mark.asyncio
async def test_delete_subject():
    def fake_api(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            204,
        )

    transport = httpx.MockTransport(fake_api)
    async with StudyOpsAPIClient(
        "http://test/api/",
        transport=transport,
    ) as api:
        await api.delete_subject(subject_id=2)

    assert True  # If no exception is raised, the test passes


@pytest.mark.asyncio
async def test_list_sessions():
    def fake_api(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json=[
                {
                    "id": 1,
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
                        "title": "Study Sorting Algorithms",
                        "description": "Review merge sort and quicksort, then solve practice problems.",
                        "task_type": "study",
                        "task_status": "in_progress",
                        "task_priority": "high",
                        "estimated_minutes": 120,
                        "due_date": "2026-08-30T18:00:00Z",
                        "created_at": "2026-08-25T10:00:00Z",
                        "updated_at": "2026-08-27T14:30:00Z",
                    },
                    "start_at": "2026-08-28T10:00:00Z",
                    "end_at": "2026-08-28T11:00:00Z",
                    "status": "scheduled",
                    "created_at": "2026-08-28T09:30:00Z",
                    "updated_at": "2026-08-28T09:30:00Z",
                }
            ],
        )

    transport = httpx.MockTransport(fake_api)

    async with StudyOpsAPIClient(
        "http://test/api/",
        transport=transport,
    ) as api:
        sessions = await api.list_sessions()

    assert len(sessions) == 1
    assert sessions[0].id == 1
    assert sessions[0].user == 10


@pytest.mark.asyncio
async def test_get_study_session():
    def fake_api(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "id": 1,
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
                    "title": "Study Sorting Algorithms",
                    "description": "Review merge sort and quicksort, then solve practice problems.",
                    "task_type": "study",
                    "task_status": "in_progress",
                    "task_priority": "high",
                    "estimated_minutes": 120,
                    "due_date": "2026-08-30T18:00:00Z",
                    "created_at": "2026-08-25T10:00:00Z",
                    "updated_at": "2026-08-27T14:30:00Z",
                },
                "start_at": "2026-08-28T10:00:00Z",
                "end_at": "2026-08-28T11:00:00Z",
                "status": "scheduled",
                "created_at": "2026-08-28T09:30:00Z",
                "updated_at": "2026-08-28T09:30:00Z",
            },
        )

    transport = httpx.MockTransport(fake_api)

    async with StudyOpsAPIClient(
        "http://test/api/",
        transport=transport,
    ) as api:
        session = await api.get_session(session_id=1)

    assert session.id == 1
    assert session.user == 10


@pytest.mark.asyncio
async def test_create_study_session():
    def fake_api(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert (
            request.url.path == "/api/study_session/"
        )  # checking if the request is correct
        assert json.loads(
            request.content
        ) == {  # checking if the request body is correct (serialized to JSON)
            "subject_id": 2,
            "task_id": 3,
            "start_at": "2026-08-29T10:00:00Z",
            "end_at": "2026-08-29T11:00:00Z",
            "status": "scheduled",
        }
        return httpx.Response(  # returning a mock response with the expected data
            201,
            json=session_response_data(
                start_at="2026-08-29T10:00:00Z",
                end_at="2026-08-29T11:00:00Z",
            ),
        )

    transport = httpx.MockTransport(fake_api)

    async with StudyOpsAPIClient(
        "http://test/api/",
        transport=transport,
    ) as api:
        created = await api.create_session(
            StudySessionCreate(
                subject_id=2,
                task_id=3,
                start_at="2026-08-29T10:00:00Z",
                end_at="2026-08-29T11:00:00Z",
            )
        )

    assert created.id == 1
    assert created.subject.id == 2
    assert created.task is not None
    assert created.task.id == 3
    assert created.status.value == "scheduled"


@pytest.mark.asyncio
async def test_update_study_session():
    def fake_api(request: httpx.Request) -> httpx.Response:
        assert request.method == "PATCH"
        assert request.url.path == "/api/study_session/1/"
        assert json.loads(request.content) == {
            "start_at": "2026-08-29T12:00:00Z",
            "end_at": "2026-08-29T13:30:00Z",
            "status": "completed",
        }
        return httpx.Response(
            200,
            json=session_response_data(
                start_at="2026-08-29T12:00:00Z",
                end_at="2026-08-29T13:30:00Z",
                status="completed",
            ),
        )

    transport = httpx.MockTransport(fake_api)

    async with StudyOpsAPIClient(
        "http://test/api/",
        transport=transport,
    ) as api:
        updated = await api.update_session(
            session_id=1,
            changes=StudySessionUpdate(
                start_at="2026-08-29T12:00:00Z",
                end_at="2026-08-29T13:30:00Z",
                status="completed",
            ),
        )

    assert updated.id == 1
    assert updated.status.value == "completed"
    assert updated.start_at.hour == 12
    assert updated.end_at.hour == 13
    assert updated.end_at.minute == 30


@pytest.mark.asyncio
async def test_delete_study_session():
    def fake_api(request: httpx.Request) -> httpx.Response:
        assert request.method == "DELETE"
        assert request.url.path == "/api/study_session/1/"
        return httpx.Response(204)

    transport = httpx.MockTransport(fake_api)

    async with StudyOpsAPIClient(
        "http://test/api/",
        transport=transport,
    ) as api:
        result = await api.delete_session(session_id=1)

    assert result is None


@pytest.mark.asyncio
async def test_get_preferences():
    def fake_api(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/study_preference/me"
        return httpx.Response(200, json=preference_response_data())

    transport = httpx.MockTransport(fake_api)

    async with StudyOpsAPIClient(
        "http://test/api/",
        transport=transport,
    ) as api:
        preferences = await api.get_preferences()

    assert preferences.timezone == "Asia/Beirut"
    assert preferences.earliest_study_time.hour == 8
    assert preferences.latest_study_time.hour == 22
    assert preferences.preferred_session_minutes == 45
    assert preferences.buffer_minutes == 10


@pytest.mark.asyncio
async def test_update_preferences():
    def fake_api(request: httpx.Request) -> httpx.Response:
        assert request.method == "PATCH"
        assert request.url.path == "/api/study_preference/me"
        assert json.loads(request.content) == {
            "preferred_session_minutes": 50,
            "buffer_minutes": 15,
        }
        return httpx.Response(
            200,
            json=preference_response_data(
                preferred_session_minutes=50,
                buffer_minutes=15,
            ),
        )

    transport = httpx.MockTransport(fake_api)

    async with StudyOpsAPIClient(
        "http://test/api/",
        transport=transport,
    ) as api:
        preferences = await api.update_preferences(
            StudyPreferenceUpdate(
                preferred_session_minutes=50,
                buffer_minutes=15,
            )
        )

    assert preferences.preferred_session_minutes == 50
    assert preferences.buffer_minutes == 15
