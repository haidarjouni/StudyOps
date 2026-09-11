import pytest
from langchain.messages import AIMessage, HumanMessage
from test_draft_schedule import make_session, make_task
from test_schedule_validation import make_constraints

from nodes import revise_draft_schedule
from schemas import Draft, DraftSchedule, PlanningSubject, ValidationNote


class StructuredOutputModel:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    async def ainvoke(self, messages):
        self.calls.append(messages)
        return next(self.responses)


def make_state(**changes):
    draft_schedule = DraftSchedule(
        drafts=[Draft(task=make_task(), study_sessions=[make_session()])]
    )
    values = {
        "messages": [HumanMessage(content="Make a database exam study plan")],
        "draft_schedule": draft_schedule,
        "planning_constraints": make_constraints(),
        "subjects": [
            PlanningSubject(
                id=4,
                name="Database Systems",
                code="DB101",
                semester=1,
            )
        ],
        "validation_notes": [
            ValidationNote(
                code="period_extension",
                message="The session extends beyond the available period.",
                draft_task_id="database_exam",
                draft_session_id="database_exam_session_1",
            )
        ],
        "schedule_revision_count": 0,
        "user_revision_request": None,
    }
    values.update(changes)
    return values


@pytest.mark.asyncio
async def test_revision_returns_parsed_schedule_and_increments_count():
    revised_schedule = make_state()["draft_schedule"]
    model = StructuredOutputModel(
        [
            {
                "parsed": revised_schedule,
                "parsing_error": None,
                "raw": AIMessage(content=""),
            }
        ]
    )

    result = await revise_draft_schedule(make_state(), model)

    assert result == {
        "draft_schedule": revised_schedule,
        "schedule_revision_count": 1,
        "validation_notes": [],
        "user_revision_request": None,
    }


@pytest.mark.asyncio
async def test_revision_retries_invalid_structured_output():
    revised_schedule = make_state()["draft_schedule"]
    model = StructuredOutputModel(
        [
            {
                "parsed": None,
                "parsing_error": ValueError("invalid draft"),
                "raw": AIMessage(content="{}"),
            },
            {
                "parsed": revised_schedule,
                "parsing_error": None,
                "raw": AIMessage(content=""),
            },
        ]
    )

    result = await revise_draft_schedule(make_state(), model)

    assert result["draft_schedule"] == revised_schedule
    assert result["schedule_revision_count"] == 1
    assert len(model.calls) == 2


@pytest.mark.asyncio
async def test_revision_rejects_a_fourth_attempt():
    model = StructuredOutputModel([])

    with pytest.raises(ValueError, match="already been revised three times"):
        await revise_draft_schedule(
            make_state(schedule_revision_count=3),
            model,
        )

    assert model.calls == []


@pytest.mark.asyncio
async def test_user_feedback_revision_does_not_increment_validation_count():
    revised_schedule = make_state()["draft_schedule"]
    model = StructuredOutputModel(
        [
            {
                "parsed": revised_schedule,
                "parsing_error": None,
                "raw": AIMessage(content=""),
            }
        ]
    )
    state = make_state(
        validation_notes=[],
        user_revision_request="Move the session to the afternoon",
        schedule_revision_count=2,
    )

    result = await revise_draft_schedule(state, model)

    assert result["schedule_revision_count"] == 2
    assert result["validation_notes"] == []
    assert result["user_revision_request"] is None
    assert "Move the session to the afternoon" in model.calls[0][0].content


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("validation_notes", "user_revision_request"),
    [([], None), (make_state()["validation_notes"], "Change the schedule")],
)
async def test_revision_requires_exactly_one_instruction_source(
    validation_notes,
    user_revision_request,
):
    model = StructuredOutputModel([])

    with pytest.raises(ValueError, match="Exactly one"):
        await revise_draft_schedule(
            make_state(
                validation_notes=validation_notes,
                user_revision_request=user_revision_request,
            ),
            model,
        )

    assert model.calls == []
