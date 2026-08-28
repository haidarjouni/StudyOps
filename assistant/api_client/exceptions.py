from typing import Any


class APIClientError(Exception):
    """Base exception for StudyOps API-client failures."""


class APITransportError(APIClientError):
    """The API could not be reached."""


class APIAuthenticationError(APIClientError):
    """Authentication failed or expired."""


class APIResponseError(APIClientError):
    """The API returned an unsuccessful HTTP response."""

    def __init__(self, status_code: int, detail: Any) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"StudyOps API returned HTTP {status_code}: {detail}")


class APIValidationError(APIClientError):
    """The API response did not match the expected Pydantic schema."""
