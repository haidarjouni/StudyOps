# assistant/api_client/client.py

from typing import Any, TypeVar

import httpx
from pydantic import TypeAdapter, ValidationError

from schemas import (StudyPreference, StudyPreferenceUpdate, StudySession,
                     StudySessionCreate, StudySessionUpdate, StudyTask,
                     StudyTaskCreate, StudyTaskUpdate, Subject, SubjectCreate,
                     SubjectUpdate)

from .exceptions import (APIAuthenticationError, APIResponseError,
                         APITransportError, APIValidationError)

T = TypeVar("T")


class StudyOpsAPIClient:
    """A client for interacting with the StudyOps API."""

    def __init__(
        self,
        base_url: str,
        *,
        access_token: str | None = None,
        refresh_token: str | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        cookies: dict[str, str] = {}

        if access_token:
            cookies["access_token"] = access_token

        if refresh_token:
            cookies["refresh_token"] = refresh_token

        self._http = httpx.AsyncClient(  # initializing the HTTP client with the provided base URL, headers, cookies, and timeout settings
            base_url=base_url.rstrip("/") + "/",
            headers={"Accept": "application/json"},
            cookies=cookies,
            timeout=httpx.Timeout(
                timeout=10.0,
                connect=3.0,
                pool=3.0,
            ),
            follow_redirects=False,
            transport=transport,
        )

    # async context manager methods
    async def __aenter__(self) -> "StudyOpsAPIClient":
        return self

    # for exit when error or normal exit
    async def __aexit__(self, *args: object) -> None:
        await self.aclose()

    # for closing the HTTP client
    async def aclose(self) -> None:
        await self._http.aclose()

    async def _request(  # abstracted way to make HTTP requests to the StudyOps API, handling errors and validating responses
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        try:
            response = await self._http.request(
                method,
                path,
                **kwargs,
            )  # call the request method of the HTTP client with the specified method, path, and any additional keyword arguments

        except (
            httpx.RequestError
        ) as exc:  # if http error/ timeout/ connection error in request, raise APITransportError with the error message
            raise APITransportError(f"Could not reach the StudyOps API: {exc}") from exc

        if (
            response.status_code == 401
        ):  # 401 unauthorized error, raise APIAuthenticationError indicating that the authentication is missing or expired
            raise APIAuthenticationError(
                "StudyOps authentication is missing or expired"
            )

        if (
            response.is_error
        ):  # if api error found other than 401, raise APIResponseError with the status code and error detail extracted from the response
            raise APIResponseError(  # raise APIResponseError with the status code and error detail extracted from the response
                status_code=response.status_code,
                detail=self._error_detail(response),
            )

        return response

    @staticmethod
    def _error_detail(response: httpx.Response) -> Any:
        try:
            return (
                response.json()
            )  # attempts to parse the response as JSON and return the parsed data
        except ValueError:
            return response.text[
                :500
            ]  # if failed to parse as JSON, return the first 500 characters of the response text as a fallback error detail

    # The method attempts to parse the response as JSON and validate it against the provided adapter. If the response is not valid JSON or does not match the expected structure, it raises an APIValidationError
    @staticmethod
    def _validate(
        response: httpx.Response, adapter: TypeAdapter[T]
    ) -> (
        T
    ):  # adapter is expected to be a TypeAdapter instance that defines the expected data structure for the response.
        try:
            data = response.json()
        except ValueError as exc:
            raise APIValidationError(
                "StudyOps API returned invalid JSON"
            ) from exc  # if the response is not valid JSON, raise an APIValidationError indicating that the StudyOps API returned invalid JSON

        try:
            return adapter.validate_python(data)  # uses the adpter validation method
        except ValidationError as exc:
            raise APIValidationError(  # if the response data does not match the expected structure defined by the adapter, raise an APIValidationError with a message indicating that the StudyOps API response was unexpected
                f"Unexpected StudyOps API response: {exc}"
            ) from exc

    async def list_subjects(self) -> list[Subject]:
        response = await self._request("GET", "subject/")
        return self._validate(
            response, TypeAdapter(list[Subject])
        )  # sends a get request to subject then validates and returns the response as a list

    async def get_subject(self, subject_id: int) -> Subject:
        response = await self._request(
            "GET",
            f"subject/{subject_id}/",
        )
        return self._validate(
            response, TypeAdapter(Subject)
        )  # sends a get request to subject with the specified id then validates and returns the response as a Subject object

    async def create_subject(
        self,
        subject: SubjectCreate,
    ) -> Subject:
        response = await self._request(
            "POST",
            "subject/",
            json=subject.model_dump(
                mode="json",
                exclude_none=True,
            ),
        )
        return self._validate(
            response, TypeAdapter(Subject)
        )  # sends a post request to create a new subject then validates and returns the response as a Subject object

    async def update_subject(
        self,
        subject_id: int,
        changes: SubjectUpdate,
    ) -> Subject:
        response = await self._request(
            "PATCH",
            f"subject/{subject_id}/",
            json=changes.model_dump(
                mode="json",
                exclude_unset=True,  # remove anything that is not set to avoid sending unnecessary data in the request
            ),
        )
        return self._validate(
            response, TypeAdapter(Subject)
        )  # sends a patch request to update the subject with the specified id then validates and returns the response as a Subject object

    async def delete_subject(self, subject_id: int) -> None:
        await self._request(
            "DELETE",
            f"subject/{subject_id}/",
        )

    async def list_sessions(
        self,
        *,
        status: str | None = None,
        subject: int | None = None,
        window_start: str | None = None,
        window_end: str | None = None,
    ) -> list[StudySession]:
        params = {
            "status": status,
            "subject": subject,
            "end_at__gt": window_start,
            "start_at__lt": window_end,
        }
        response = await self._request(
            "GET",
            "study_session/",
            params={key: value for key, value in params.items() if value is not None},
        )
        return self._validate(
            response, TypeAdapter(list[StudySession])
        )  # sends a get request to study_session then validates and returns the response as a list of StudySession objects

    async def get_session(self, session_id: int) -> StudySession:
        response = await self._request(
            "GET",
            f"study_session/{session_id}/",
        )
        return self._validate(
            response, TypeAdapter(StudySession)
        )  # sends a get request to study_session with the specified id then validates and returns the response as a StudySession object

    async def create_session(
        self,
        session: StudySessionCreate,
    ) -> StudySession:
        response = await self._request(
            "POST",
            "study_session/",
            json=session.model_dump(
                mode="json",
                exclude_none=True,
            ),
        )
        return self._validate(
            response, TypeAdapter(StudySession)
        )  # sends a post request to create a new study session then validates and returns the response as a StudySession object

    async def delete_session(self, session_id: int) -> None:
        await self._request(
            "DELETE",
            f"study_session/{session_id}/",
        )  # sends a delete request to delete the study session with the specified id

    async def update_session(
        self,
        session_id: int,
        changes: StudySessionUpdate,
    ) -> StudySession:
        response = await self._request(
            "PATCH",
            f"study_session/{session_id}/",
            json=changes.model_dump(
                mode="json",
                exclude_unset=True,
            ),
        )
        return self._validate(
            response, TypeAdapter(StudySession)
        )  # sends a patch request to update the study session with the specified id then validates and returns the response as a StudySession object

    async def get_preferences(self) -> StudyPreference:
        response = await self._request("GET", "study_preference/me")
        return self._validate(
            response, TypeAdapter(StudyPreference)
        )  # sends a get request to retrieve the current user's study preferences then validates and returns the response as a StudyPreference object

    async def update_preferences(
        self,
        changes: StudyPreferenceUpdate,
    ) -> StudyPreference:
        response = await self._request(
            "PATCH",
            "study_preference/me",
            json=changes.model_dump(
                mode="json",
                exclude_unset=True,
            ),
        )
        return self._validate(
            response, TypeAdapter(StudyPreference)
        )  # sends a patch request to update the current user's study preferences then validates and returns the response as a StudyPreference object

    async def list_study_tasks(
        self,
        *,
        task_status: str | None = None,
        subject: int | None = None,
        due_from: str | None = None,
        due_to: str | None = None,
    ) -> list[StudyTask]:
        params = {
            "task_status": task_status,
            "subject": subject,
            "due_date__gte": due_from,
            "due_date__lte": due_to,
        }
        response = await self._request("GET", "study_task/", params={key: value for key, value in params.items() if value is not None})  # sends a get request to retrieve the list of study tasks with optional filtering parameters for task status, subject, and due date range
        return self._validate(
            response, TypeAdapter(list[StudyTask])
        )  # sends a get request to retrieve the list of study tasks then validates and returns the response as a list of StudyTask objects

    async def get_study_task(
        self,
        study_task_id: int,
    ) -> StudyTask:
        response = await self._request(
            "GET",
            f"study_task/{study_task_id}/",
        )
        return self._validate(
            response, TypeAdapter(StudyTask)
        )  # sends a get request to retrieve the study task with the specified id then validates and returns the response as a StudyTask object

    async def create_study_task(
        self,
        study_task: StudyTaskCreate,
    ) -> StudyTask:
        response = await self._request(
            "POST",
            "study_task/",
            json=study_task.model_dump(
                mode="json",
                exclude_none=True,
            ),
        )
        return self._validate(
            response, TypeAdapter(StudyTask)
        )  # sends a post request to create a new study task then validates and returns the response as a StudyTask object

    async def update_study_task(
        self,
        study_task_id: int,
        changes: StudyTaskUpdate,
    ) -> StudyTask:
        response = await self._request(
            "PATCH",
            f"study_task/{study_task_id}/",
            json=changes.model_dump(
                mode="json",
                exclude_unset=True,
            ),
        )
        return self._validate(
            response, TypeAdapter(StudyTask)
        )  # sends a patch request to update the study task with the specified id then validates and returns the response as a StudyTask object

    async def delete_study_task(
        self,
        study_task_id: int,
    ) -> None:
        await self._request(
            "DELETE",
            f"study_task/{study_task_id}/",
        )  # sends a delete request to delete the study task with the specified id
