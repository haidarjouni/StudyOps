import json

import httpx
import pytest

from api_client.client import StudyOpsAPIClient
from api_client.exceptions import APIResponseError
from schemas.study_preference import StudyPreferenceUpdate
from schemas.study_session import StudySessionCreate, StudySessionUpdate
from schemas.study_task import StudyTaskCreate, StudyTaskUpdate
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


def study_task_response_data(**changes) -> dict:
    data = {
        "id": 4,
        "user": 10,
        "subject": 2,
        "title": "Complete Programming Assignment",
        "description": "Implement the required features and write unit tests.",
        "task_type": "assignment",
        "task_status": "todo",
        "task_priority": "high",
        "estimated_minutes": 90,
        "due_date": "2026-09-10T20:00:00Z",
        "created_at": "2026-08-29T10:00:00Z",
        "updated_at": "2026-08-29T10:00:00Z",
    }
    data.update(changes) # takes key value kwarg and cahnges the default values in data dict
    return data


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


@pytest.mark.asyncio
async def test_list_study_tasks():
    def fake_api(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/study_task/"
        return httpx.Response(200, json=[study_task_response_data()])

    async with StudyOpsAPIClient(
        "http://test/api/",
        transport=httpx.MockTransport(fake_api),
    ) as api:
        tasks = await api.list_study_tasks()

    assert len(tasks) == 1
    assert tasks[0].id == 4
    assert tasks[0].task_priority.value == "high"


@pytest.mark.asyncio
async def test_get_study_task():
    def fake_api(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/study_task/4/"
        return httpx.Response(200, json=study_task_response_data())

    async with StudyOpsAPIClient(
        "http://test/api/",
        transport=httpx.MockTransport(fake_api),
    ) as api:
        task = await api.get_study_task(study_task_id=4)

    assert task.id == 4
    assert task.subject == 2
    assert task.title == "Complete Programming Assignment"


@pytest.mark.asyncio
async def test_create_study_task():
    def fake_api(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert request.url.path == "/api/study_task/"

        payload = json.loads(request.content)
        assert payload["subject"] == 2
        assert payload["title"] == "Review graph algorithms"

        return httpx.Response(
            201,
            json=study_task_response_data(
                title="Review graph algorithms",
                description="Review BFS and DFS, then solve practice problems.",
                task_type="study",
                task_priority="medium",
                estimated_minutes=60,
            ), #returned updated data from the API with the new title and description
        )

    async with StudyOpsAPIClient(
        "http://test/api/",
        transport=httpx.MockTransport(fake_api),
    ) as api:
        task = await api.create_study_task(
            StudyTaskCreate(
                subject=2,
                title="Review graph algorithms",
                description="Review BFS and DFS, then solve practice problems.",
                task_type="study",
                estimated_minutes=60,
                due_date="2026-09-10T20:00:00Z",
            )
        )

    assert task.id == 4
    assert task.title == "Review graph algorithms"
    assert task.task_status.value == "todo"


@pytest.mark.asyncio
async def test_update_study_task():
    def fake_api(request: httpx.Request) -> httpx.Response:
        assert request.method == "PATCH"
        assert request.url.path == "/api/study_task/4/"
        assert json.loads(request.content) == {
            "task_status": "done",
            "task_priority": "low",
        } # checking if the request body is correct (serialized to JSON)

        return httpx.Response(
            200,
            json=study_task_response_data(
                task_status="done",
                task_priority="low",
            ), # returned updated data from the API with the new task_status and task_priority
        )

    async with StudyOpsAPIClient(
        "http://test/api/",
        transport=httpx.MockTransport(fake_api),
    ) as api:
        task = await api.update_study_task(
            study_task_id=4,
            changes=StudyTaskUpdate(
                task_status="done",
                task_priority="low",
            ),
        )

    assert task.task_status.value == "done"
    assert task.task_priority.value == "low"


@pytest.mark.asyncio
async def test_delete_study_task():
    def fake_api(request: httpx.Request) -> httpx.Response:
        assert request.method == "DELETE"
        assert request.url.path == "/api/study_task/4/"
        return httpx.Response(204)

    async with StudyOpsAPIClient(
        "http://test/api/",
        transport=httpx.MockTransport(fake_api),
    ) as api:
        result = await api.delete_study_task(study_task_id=4) # calling the delete_study_task method of the API client

    assert result is None
