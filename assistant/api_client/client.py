# assistant/api_client/client.py

from typing import Any, TypeVar

import httpx
from pydantic import TypeAdapter, ValidationError
from schemas import (
    StudyPreference,
    StudyPreferenceUpdate,
    StudySession,
    StudySessionCreate,
    StudySessionUpdate,
    Subject,
    SubjectCreate,
    SubjectUpdate,
)

from .exceptions import (
    APIAuthenticationError,
    APIResponseError,
    APITransportError,
    APIValidationError,
)

T = TypeVar("T")


class StudyOpsAPIClient:
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

        self._http = httpx.AsyncClient(
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

    async def __aenter__(self) -> "StudyOpsAPIClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    async def _request(
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
            )
        except httpx.RequestError as exc:
            raise APITransportError(f"Could not reach the StudyOps API: {exc}") from exc

        if response.status_code == 401:
            raise APIAuthenticationError(
                "StudyOps authentication is missing or expired"
            )

        if response.is_error:
            raise APIResponseError(
                status_code=response.status_code,
                detail=self._error_detail(response),
            )

        return response

    @staticmethod
    def _error_detail(response: httpx.Response) -> Any:
        try:
            return response.json()
        except ValueError:
            return response.text[:500]

    @staticmethod
    def _validate(response: httpx.Response, adapter: TypeAdapter[T]) -> T:
        try:
            data = response.json()
        except ValueError as exc:
            raise APIValidationError("StudyOps API returned invalid JSON") from exc

        try:
            return adapter.validate_python(data)
        except ValidationError as exc:
            raise APIValidationError(
                f"Unexpected StudyOps API response: {exc}"
            ) from exc

    async def list_subjects(self) -> list[Subject]:
        response = await self._request("GET", "subject/")
        return self._validate(response, TypeAdapter(list[Subject]))

    async def get_subject(self, subject_id: int) -> Subject:
        response = await self._request(
            "GET",
            f"subject/{subject_id}/",
        )
        return self._validate(response, TypeAdapter(Subject))

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
        return self._validate(response, TypeAdapter(Subject))

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
                exclude_unset=True,
            ),
        )
        return self._validate(response, TypeAdapter(Subject))

    async def delete_subject(self, subject_id: int) -> None:
        await self._request(
            "DELETE",
            f"subject/{subject_id}/",
        )

    async def list_sessions(self) -> list[StudySession]:
        response = await self._request("GET", "study_session/")
        return self._validate(response, TypeAdapter(list[StudySession]))

    async def get_session(self, session_id: int) -> StudySession:
        response = await self._request(
            "GET",
            f"study_session/{session_id}/",
        )
        return self._validate(response, TypeAdapter(StudySession))

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
        return self._validate(response, TypeAdapter(StudySession))

    async def delete_session(self, session_id: int) -> None:
        await self._request(
            "DELETE",
            f"study_session/{session_id}/",
        )

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
        return self._validate(response, TypeAdapter(StudySession))

    async def get_preferences(self) -> StudyPreference:
        response = await self._request("GET", "study_preference/me")
        return self._validate(response, TypeAdapter(StudyPreference))

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
        return self._validate(response, TypeAdapter(StudyPreference))
