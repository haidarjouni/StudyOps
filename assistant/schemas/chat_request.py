from typing import Self
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, Field, field_validator, model_validator


class ChatRequest(BaseModel):
    thread_id: str = Field(min_length=1)
    time_zone: str = "Asia/Beirut"
    user_input: str | None = None
    command: dict[str, str] | None = None

    @field_validator("time_zone")
    @classmethod
    def valid_timezone(cls, value: str) -> str:
        # checks if timezone is a valid IANA timezone
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError("time_zone must be a valid IANA timezone")
        return value

    @model_validator(mode="after")
    def valid_message(self) -> Self:
        # empty request raise error
        if (self.user_input is None) == (self.command is None):
            raise ValueError("Supply exactly one of user_input or command")
        # if user_input is not None, it must not be blank
        if self.user_input is not None and not self.user_input.strip():
            raise ValueError("user_input must not be blank")
        # if command is not None, it must have a valid action and feedback if action is edit
        if self.command is not None:
            if self.command.get("action") not in {"approve", "edit", "cancel"}:
                raise ValueError("command.action must be approve, edit, or cancel")
            if (
                self.command["action"] == "edit"
                and not self.command.get("feedback", "").strip()
            ):
                raise ValueError("An edit command requires feedback")
        return self
