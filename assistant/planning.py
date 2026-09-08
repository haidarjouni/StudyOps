"""Deterministic calculations used by the study-planning graph."""

from collections import defaultdict
from datetime import date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from pydantic import AwareDatetime, BaseModel, ConfigDict, TypeAdapter, model_validator

from schemas import (
    DailyPlanningPeriod,
    PlanningConstraints,
    ResolvedPlanningRequest,
    StudyPreference,
)


class _ExistingSessionPeriod(BaseModel):
    """The session fields needed to calculate planning constraints."""

    model_config = ConfigDict(extra="ignore")

    start_at: AwareDatetime
    end_at: AwareDatetime

    @model_validator(mode="after")
    def valid_range(self):
        if self.end_at <= self.start_at:
            raise ValueError("Session end must be later than its start")
        return self


_SESSION_LIST_ADAPTER = TypeAdapter(list[_ExistingSessionPeriod])


def _group_sessions_by_local_date(
    sessions: list[_ExistingSessionPeriod],
    user_timezone: ZoneInfo,
) -> dict[date, list[_ExistingSessionPeriod]]:
    grouped: dict[date, list[_ExistingSessionPeriod]] = defaultdict(list)

    for session in sessions:
        local_session = _ExistingSessionPeriod(
            start_at=session.start_at.astimezone(user_timezone),
            end_at=session.end_at.astimezone(user_timezone),
        )  # convert the session times to the user's timezone

        # A cross-midnight session occupies every local date it overlaps.
        session_date = (
            local_session.start_at.date()
        )  # get the local date of the session start
        final_date = local_session.end_at.date()
        while (
            session_date <= final_date
        ):  # because a session can span multiple days, we need to check each day it overlaps
            day_start = datetime.combine(
                session_date, time.min, user_timezone
            )  # get the start of the day in the user's timezone
            next_day_start = datetime.combine(  # get the start of the next day in the user's timezone
                session_date + timedelta(days=1),
                time.min,
                user_timezone,
            )
            if (
                local_session.start_at < next_day_start
                and local_session.end_at > day_start
            ):  # if the session overlaps with this day, add it to the list for that day
                grouped[session_date].append(
                    local_session
                )  # add the session to the list for this date
            session_date += timedelta(days=1)  # move to the next date

    return grouped


def build_planning_constraints(
    planning_request: ResolvedPlanningRequest,
    preferences: StudyPreference,
    sessions_data: Any,
    *,
    current_datetime: datetime | None = None,
) -> PlanningConstraints:
    """Build append-only daily planning periods from validated source data."""

    user_timezone = ZoneInfo(preferences.timezone)
    window_start = planning_request.window_start.astimezone(user_timezone)
    window_end = planning_request.window_end.astimezone(user_timezone)

    now = current_datetime or datetime.now(user_timezone)
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("Current datetime must be timezone-aware")
    now = now.astimezone(user_timezone)

    sessions = _SESSION_LIST_ADAPTER.validate_python(sessions_data)
    sessions_by_date = _group_sessions_by_local_date(sessions, user_timezone)

    daily_periods: list[DailyPlanningPeriod] = []
    planning_date = window_start.date()

    while datetime.combine(planning_date, time.min, user_timezone) < window_end:
        preferred_start = datetime.combine(
            planning_date,
            preferences.earliest_study_time,
            user_timezone,
        )
        preferred_end = datetime.combine(
            planning_date,
            preferences.latest_study_time,
            user_timezone,
        )

        start_candidates = [preferred_start, window_start]
        sessions_for_day = sessions_by_date.get(planning_date, [])
        if sessions_for_day:
            latest_session_end = max(session.end_at for session in sessions_for_day)
            start_candidates.append(
                latest_session_end + timedelta(minutes=preferences.buffer_minutes)
            )

        if planning_date == now.date():
            start_candidates.append(now)

        start_at = max(start_candidates)
        end_at = min(preferred_end, window_end)

        if start_at < end_at:
            daily_periods.append(
                DailyPlanningPeriod(
                    date=planning_date,
                    start_at=start_at,
                    end_at=end_at,
                )
            )

        planning_date += timedelta(days=1)

    return PlanningConstraints(
        timezone=preferences.timezone,
        window_start=window_start,
        window_end=window_end,
        preferred_session_minutes=preferences.preferred_session_minutes,
        buffer_minutes=preferences.buffer_minutes,
        daily_periods=daily_periods,
    )
