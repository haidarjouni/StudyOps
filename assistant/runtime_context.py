from dataclasses import dataclass


@dataclass
class RequestContext:
    """Per-request credentials and timezone supplied by the application."""

    # This is filled during runtime with the context needed for the current
    # request, including any access tokens, refresh tokens, and timezone
    # information.
    access_token: str | None
    refresh_token: str | None
    timezone: str = "UTC"
