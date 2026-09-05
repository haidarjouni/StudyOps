from datetime import datetime

from nodes import validate_schedule
from schemas import (DailyPlanningPeriod, Draft, DraftSchedule,
                     PlanningConstraints)

from test_draft_schedule import make_session, make_task


def make_constraints(**changes) -> PlanningConstraints:
    values = {
        "timezone": "Asia/Beirut",
        "window_start": datetime.fromisoformat("2026-09-05T09:00:00+03:00"),
        "window_end": datetime.fromisoformat("2026-09-05T18:00:00+03:00"),
        "preferred_session_minutes": 45,
        "buffer_minutes": 15,
        "daily_periods": [
            DailyPlanningPeriod(
                date="2026-09-05",
                start_at="2026-09-05T09:00:00+03:00",
                end_at="2026-09-05T17:00:00+03:00",
            )
        ],
    }
    values.update(changes)
    return PlanningConstraints(**values)


def validate(drafts, *, constraints=None, revision_count=0):
    return validate_schedule(
        {
            "draft_schedule": DraftSchedule(drafts=drafts),
            "planning_constraints": constraints or make_constraints(),
            "schedule_revision_count": revision_count,
        }
    )["validation_notes"]


def test_accepts_a_valid_schedule():
    notes = validate(
        [Draft(task=make_task(), study_sessions=[make_session()])]
    )

    assert notes == []


def test_rejects_a_session_starting_outside_available_periods():
    notes = validate(
        [
            Draft(
                task=make_task(),
                study_sessions=[
                    make_session(
                        start_at="2026-09-05T08:00:00+03:00",
                        end_at="2026-09-05T08:45:00+03:00",
                    )
                ],
            )
        ],
        constraints=make_constraints(
            window_start="2026-09-05T07:00:00+03:00"
        ),
    )

    assert [note.code for note in notes] == ["outside_available_period"]


def test_rejects_a_session_outside_the_planning_window():
    notes = validate(
        [
            Draft(
                task=make_task(),
                study_sessions=[
                    make_session(
                        start_at="2026-09-05T17:30:00+03:00",
                        end_at="2026-09-05T18:30:00+03:00",
                    )
                ],
            )
        ]
    )

    assert [note.code for note in notes] == ["outside_planning_window"]


def test_period_extension_is_only_reported_before_first_revision():
    draft = Draft(
        task=make_task(),
        study_sessions=[
            make_session(
                start_at="2026-09-05T16:30:00+03:00",
                end_at="2026-09-05T17:30:00+03:00",
            )
        ],
    )

    assert [note.code for note in validate([draft])] == ["period_extension"]
    assert validate([draft], revision_count=1) == []


def test_reports_overlaps_and_insufficient_buffers():
    sessions = [
        make_session(
            draft_session_id="database_exam_session_1",
            start_at="2026-09-05T10:00:00+03:00",
            end_at="2026-09-05T11:00:00+03:00",
        ),
        make_session(
            draft_session_id="database_exam_session_2",
            start_at="2026-09-05T10:45:00+03:00",
            end_at="2026-09-05T11:30:00+03:00",
        ),
        make_session(
            draft_session_id="database_exam_session_3",
            start_at="2026-09-05T11:40:00+03:00",
            end_at="2026-09-05T12:00:00+03:00",
        ),
    ]

    notes = validate([Draft(task=make_task(), study_sessions=sessions)])

    assert [note.code for note in notes] == ["overlap", "insufficient_buffer"]


def test_rejects_scheduled_time_above_the_task_estimate():
    draft = Draft(
        task=make_task(estimated_minutes=30),
        study_sessions=[make_session()],
    )

    notes = validate([draft])

    assert [note.code for note in notes] == ["estimated_minutes_exceeded"]
