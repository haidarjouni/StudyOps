from dataclasses import dataclass


@dataclass
class RequestContext:
    access_token: str | None
    refresh_token: str | None
