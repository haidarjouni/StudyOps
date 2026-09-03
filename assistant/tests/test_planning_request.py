import pytest
from pydantic import ValidationError

from schemas import ResolvedPlanningRequest


def test_resolved_planning_request_accepts_an_aware_ordered_window():
    request = ResolvedPlanningRequest(
        window_start="2026-09-03T12:00:00+03:00",
        window_end="2026-09-10T00:00:00+03:00",
    )

    assert request.window_start.utcoffset() is not None
    assert request.window_end > request.window_start


@pytest.mark.parametrize(
    ("window_start", "window_end"),
    [
        ("2026-09-03T12:00:00", "2026-09-10T00:00:00+03:00"),
        ("2026-09-03T12:00:00+03:00", "2026-09-10T00:00:00"),
        ("2026-09-10T00:00:00+03:00", "2026-09-03T12:00:00+03:00"),
    ],
)
def test_resolved_planning_request_rejects_invalid_windows(
    window_start: str,
    window_end: str,
):
    with pytest.raises(ValidationError):
        ResolvedPlanningRequest(
            window_start=window_start,
            window_end=window_end,
        )
