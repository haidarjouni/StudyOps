from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from planning import build_planning_constraints
from schemas import ResolvedPlanningRequest, StudyPreference


def make_preferences() -> StudyPreference:
    return StudyPreference(
        timezone="Asia/Beirut",
        earliest_study_time="09:00",
        latest_study_time="18:00",
        preferred_session_minutes=45,
        buffer_minutes=10,
    )


def test_builds_periods_after_sessions_and_for_empty_dates():
    request = ResolvedPlanningRequest(
        window_start="2026-09-10T12:00:00+03:00",
        window_end="2026-09-12T00:00:00+03:00",
    )
    sessions = [
        {
            "id": 1,
            "start_at": "2026-09-10T13:00:00+03:00",
            "end_at": "2026-09-10T15:00:00+03:00",
        }
    ]

    constraints = build_planning_constraints(
        request,
        make_preferences(),
        sessions,
        current_datetime=datetime(2026, 9, 3, 12, tzinfo=ZoneInfo("Asia/Beirut")),
    )

    assert [period.date.isoformat() for period in constraints.daily_periods] == [
        "2026-09-10",
        "2026-09-11",
    ]
    assert constraints.daily_periods[0].start_at.isoformat() == (
        "2026-09-10T15:10:00+03:00"
    )
    assert constraints.daily_periods[0].end_at.isoformat() == (
        "2026-09-10T18:00:00+03:00"
    )
    assert constraints.daily_periods[1].start_at.isoformat() == (
        "2026-09-11T09:00:00+03:00"
    )


def test_clips_today_to_current_time():
    request = ResolvedPlanningRequest(
        window_start="2026-09-03T10:00:00+03:00",
        window_end="2026-09-04T00:00:00+03:00",
    )

    constraints = build_planning_constraints(
        request,
        make_preferences(),
        [],
        current_datetime=datetime(2026, 9, 3, 13, 30, tzinfo=ZoneInfo("Asia/Beirut")),
    )

    assert constraints.daily_periods[0].start_at.isoformat() == (
        "2026-09-03T13:30:00+03:00"
    )


def test_converts_utc_sessions_to_the_users_local_date():
    request = ResolvedPlanningRequest(
        window_start="2026-09-10T09:00:00+03:00",
        window_end="2026-09-11T00:00:00+03:00",
    )
    sessions = [
        {
            "start_at": "2026-09-10T10:00:00Z",
            "end_at": "2026-09-10T12:00:00Z",
        }
    ]

    constraints = build_planning_constraints(
        request,
        make_preferences(),
        sessions,
        current_datetime=datetime(2026, 9, 3, 12, tzinfo=ZoneInfo("Asia/Beirut")),
    )

    assert constraints.daily_periods[0].start_at.isoformat() == (
        "2026-09-10T15:10:00+03:00"
    )


def test_omits_a_date_with_no_remaining_time():
    request = ResolvedPlanningRequest(
        window_start="2026-09-10T09:00:00+03:00",
        window_end="2026-09-11T00:00:00+03:00",
    )
    sessions = [
        {
            "start_at": "2026-09-10T13:00:00+03:00",
            "end_at": "2026-09-10T18:00:00+03:00",
        }
    ]

    constraints = build_planning_constraints(
        request,
        make_preferences(),
        sessions,
        current_datetime=datetime(2026, 9, 3, 12, tzinfo=ZoneInfo("Asia/Beirut")),
    )

    assert constraints.daily_periods == []


def test_rejects_an_invalid_session_result():
    request = ResolvedPlanningRequest(
        window_start="2026-09-10T09:00:00+03:00",
        window_end="2026-09-11T00:00:00+03:00",
    )

    with pytest.raises(ValidationError):
        build_planning_constraints(
            request,
            make_preferences(),
            [{"start_at": "invalid", "end_at": "also-invalid"}],
        )
