import pytest
from pydantic import ValidationError

from schemas import DailyPlanningPeriod, PlanningConstraints


def make_constraints(**overrides):
    values = {
        "timezone": "Asia/Beirut",
        "window_start": "2026-09-03T12:00:00+03:00",
        "window_end": "2026-09-05T00:00:00+03:00",
        "preferred_session_minutes": 45,
        "buffer_minutes": 10,
        "daily_periods": [
            {
                "date": "2026-09-03",
                "start_at": "2026-09-03T13:30:00+03:00",
                "end_at": "2026-09-03T18:00:00+03:00",
            }
        ],
    }
    values.update(overrides)
    return PlanningConstraints(**values)


def test_planning_constraints_accept_valid_values():
    constraints = make_constraints()

    assert constraints.timezone == "Asia/Beirut"
    assert constraints.daily_periods[0].date.isoformat() == "2026-09-03"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("timezone", "Not/A_Timezone"),
        ("window_start", "2026-09-03T12:00:00"),
        ("window_end", "2026-09-05T00:00:00"),
        ("preferred_session_minutes", 0),
        ("buffer_minutes", -1),
    ],
)
def test_planning_constraints_reject_invalid_fields(field, value):
    with pytest.raises(ValidationError):
        make_constraints(**{field: value})


def test_daily_period_rejects_naive_or_reversed_timestamps():
    with pytest.raises(ValidationError):
        DailyPlanningPeriod(
            date="2026-09-03",
            start_at="2026-09-03T18:00:00+03:00",
            end_at="2026-09-03T13:30:00+03:00",
        )

    with pytest.raises(ValidationError):
        DailyPlanningPeriod(
            date="2026-09-03",
            start_at="2026-09-03T13:30:00",
            end_at="2026-09-03T18:00:00+03:00",
        )


def test_planning_constraints_reject_period_outside_window():
    with pytest.raises(ValidationError):
        make_constraints(
            daily_periods=[
                {
                    "date": "2026-09-03",
                    "start_at": "2026-09-03T11:00:00+03:00",
                    "end_at": "2026-09-03T18:00:00+03:00",
                }
            ]
        )


def test_planning_constraints_reject_duplicate_dates():
    period = {
        "date": "2026-09-03",
        "start_at": "2026-09-03T13:30:00+03:00",
        "end_at": "2026-09-03T18:00:00+03:00",
    }

    with pytest.raises(ValidationError):
        make_constraints(daily_periods=[period, period])


def test_planning_constraints_reject_period_for_a_different_local_date():
    with pytest.raises(ValidationError):
        make_constraints(
            daily_periods=[
                {
                    "date": "2026-09-04",
                    "start_at": "2026-09-03T13:30:00+03:00",
                    "end_at": "2026-09-03T18:00:00+03:00",
                }
            ]
        )


def test_planning_constraints_reject_period_ending_on_a_different_local_date():
    with pytest.raises(ValidationError):
        make_constraints(
            window_end="2026-09-05T12:00:00+03:00",
            daily_periods=[
                {
                    "date": "2026-09-03",
                    "start_at": "2026-09-03T23:00:00+03:00",
                    "end_at": "2026-09-04T01:00:00+03:00",
                }
            ],
        )
