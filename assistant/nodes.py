import json
from datetime import datetime, timedelta
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from api_client import StudyOpsAPIClient
from config import Config
from langchain.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END
from langgraph.runtime import Runtime
from langgraph.types import Command, interrupt
from planning import build_planning_constraints
from prompts import (
    CONTEXT_RETRIEVAL_PROMPT,
    FINAL_SUMMARY_PROMPT,
    GENERATE_DRAFT_SCHEDULE_PROMPT,
    RESOLVE_PLANNING_REQUEST_PROMPT,
    REVISE_DRAFT_SCHEDULE_PROMPT,
    REVISE_FROM_USER_FEEDBACK_PROMPT,
)
from runtime_context import RequestContext
from schemas import (PlanningSubject, ScheduleResponse, StudyPreference,
                     ValidationNote)
from state import AgentState

_MISSING = object()


def get_tool_result(state: AgentState, tool_name: str):
    """Return the latest successful result for a named tool."""

    for message in reversed(state["messages"]):
        if not isinstance(message, ToolMessage):
            continue

        if message.name != tool_name:
            continue

        if getattr(message, "status", "success") == "error":
            raise ValueError(f"{tool_name} failed: {message.content}")

        if isinstance(message.content, str):
            return json.loads(message.content)

        return message.content

    return _MISSING


def get_latest_user_request(state: AgentState) -> str:
    """Return the most recent non-empty text request from the user."""

    for message in reversed(state["messages"]):
        if not isinstance(message, HumanMessage):
            continue

        if isinstance(message.content, str) and message.content.strip():
            return message.content

    raise ValueError("Missing user planning request")


def _user_timezone(timezone_name: str) -> tuple[str, ZoneInfo]:
    """Return a valid user timezone, falling back to UTC."""

    try:
        # name of the timezone , object of the timezone
        return timezone_name, ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return "UTC", ZoneInfo("UTC")


async def resolve_planning_request(
    state: AgentState,
    runtime: Runtime[RequestContext],
    model,
):
    """Resolve the user's natural-language request to an exact planning window."""

    timezone_name, user_timezone = _user_timezone(runtime.context.timezone)
    system_message = SystemMessage(
        content=RESOLVE_PLANNING_REQUEST_PROMPT.format(
            current_datetime=datetime.now(user_timezone).isoformat(),
            timezone=timezone_name,
        )
    )

    response = await model.ainvoke([system_message, *state["messages"]])
    return {"planning_request": response}


async def retrieve_context(
    state: AgentState,
    runtime: Runtime[RequestContext],
    model,
):
    """Retrieve the tool-backed context required by the planning workflow."""

    timezone_name, user_timezone = _user_timezone(runtime.context.timezone)
    planning_request = state["planning_request"]

    system_message = SystemMessage(
        content=CONTEXT_RETRIEVAL_PROMPT.format(
            current_datetime=datetime.now(user_timezone).isoformat(),
            timezone=timezone_name,
            window_start=planning_request.window_start.isoformat(),
            window_end=planning_request.window_end.isoformat(),
        )
    )

    response = await model.ainvoke([system_message, *state["messages"]])

    return {"messages": [response]}


async def collect_constraints(
    state: AgentState,
):
    """Return the planning constraints derived from the user's request."""

    preferences_data = get_tool_result(state, "get_preferences")
    sessions_data = get_tool_result(state, "get_sessions")
    subjects_data = get_tool_result(state, "list_subjects")
    if preferences_data is _MISSING:
        raise ValueError("Missing get_preferences tool result")

    if sessions_data is _MISSING:
        raise ValueError("Missing get_sessions tool result")

    if subjects_data is _MISSING:
        raise ValueError("Missing list_subjects tool result")

    study_preferences = StudyPreference.model_validate(preferences_data)
    constraints = build_planning_constraints(
        planning_request=state["planning_request"],
        preferences=study_preferences,
        sessions_data=sessions_data,
    )
    planning_subject = [
        PlanningSubject.model_validate(subject) for subject in subjects_data
    ]

    return {
        "planning_constraints": constraints,
        "subjects": planning_subject,
    }


async def generate_draft_schedule(
    state: AgentState,
    model,
):
    """Generate a draft schedule from the user's request and planning constraints."""
    planning_constraints = state["planning_constraints"]
    subjects = state["subjects"]

    if not subjects:
        raise ValueError("Cannot generate a draft schedule without subjects")

    if not planning_constraints.daily_periods:
        raise ValueError("Cannot generate a draft schedule without available periods")

    subject_context = [
        subject.model_dump(mode="json") for subject in subjects
    ]  # turn them to json compatible format
    system_message = SystemMessage(
        content=GENERATE_DRAFT_SCHEDULE_PROMPT.format(
            user_request=get_latest_user_request(state),
            subjects=json.dumps(
                subject_context, indent=2
            ),  # convert the list of subjects to JSON
            planning_constraints=planning_constraints.model_dump_json(indent=2),
        )
    )
    messages = [system_message]
    for i in range(3):  # for retry
        response = await model.ainvoke(messages)  # run first time
        # parsing error is none if successful parsing, parsed is the parsed draft schedule
        if (
            response["parsing_error"] is None and response["parsed"] is not None
        ):  # if successful parsing
            return {"draft_schedule": response["parsed"]}

        if i < 2:
            # if failed  add the system message the raw response and human message that specifies the validation error and asks for correction
            messages = [
                system_message,
                response["raw"],  # Message containing the invalid draft
                HumanMessage(
                    content=(
                        f"Validation failed:\n{response['parsing_error']}\n"
                        "Correct the errors and return the complete DraftSchedule."
                    )
                ),
            ]
    # if failed 3 times raise error
    raise ValueError("Draft generation failed after three attempts")


def validate_schedule(state: AgentState):
    """Validate business rules that depend on the complete draft schedule."""

    schedule = state["draft_schedule"]
    constraints = state["planning_constraints"]
    revision_count = state.get("schedule_revision_count", 0)
    notes: list[ValidationNote] = []
    all_sessions = []

    for draft in schedule.drafts:
        scheduled_duration = timedelta()  # initialize scheduled_duration to zero

        for (
            session
        ) in (
            draft.study_sessions
        ):  # for each session in the list of study_sessions of the draft
            all_sessions.append(
                (draft.task.draft_task_id, session)
            )  # gets all the sessions in the schedule and adds them to a list of tuples containing the draft_task_id and the session
            scheduled_duration += session.end_at - session.start_at

            if (
                # check if the session is outside the planning window
                session.start_at < constraints.window_start
                or session.end_at > constraints.window_end
            ):
                notes.append(
                    ValidationNote(
                        code="outside_planning_window",
                        message=(
                            f"{session.draft_session_id} runs from "
                            f"{session.start_at.isoformat()} to "
                            f"{session.end_at.isoformat()}, outside the planning "
                            f"window {constraints.window_start.isoformat()} to "
                            f"{constraints.window_end.isoformat()}."
                        ),
                        draft_task_id=draft.task.draft_task_id,
                        draft_session_id=session.draft_session_id,
                    )
                )
                continue

            containing_period = next(
                (
                    # get periods that contain the session start time, if any
                    period
                    for period in constraints.daily_periods
                    if period.start_at <= session.start_at < period.end_at
                ),
                None,
            )
            # if no containing period is found, the session is outside the available periods
            if containing_period is None:
                notes.append(
                    ValidationNote(
                        code="outside_available_period",
                        message=(
                            f"{session.draft_session_id} starts at "
                            f"{session.start_at.isoformat()}, outside every "
                            "available planning period."
                        ),
                        draft_task_id=draft.task.draft_task_id,
                        draft_session_id=session.draft_session_id,
                    )
                )
            # if the session ends after the containing period and this is the first revision, add a period_extension note
            elif session.end_at > containing_period.end_at and revision_count == 0:
                extension_minutes = int(
                    (session.end_at - containing_period.end_at).total_seconds() // 60
                )
                notes.append(
                    ValidationNote(
                        code="period_extension",
                        message=(
                            f"{session.draft_session_id} ends at "
                            f"{session.end_at.isoformat()}, extending "
                            f"{extension_minutes} minutes beyond the available "
                            f"period ending at {containing_period.end_at.isoformat()}."
                        ),
                        draft_task_id=draft.task.draft_task_id,
                        draft_session_id=session.draft_session_id,
                    )
                )
        # gets estimated duration of the task in minutes and converts it to timedelta
        estimated_duration = timedelta(minutes=draft.task.estimated_minutes)
        # if the total scheduled duration exceeds the estimated duration, add a note
        if scheduled_duration > estimated_duration:
            scheduled_minutes = int(scheduled_duration.total_seconds() // 60)
            notes.append(
                ValidationNote(
                    code="estimated_minutes_exceeded",
                    message=(
                        f"{draft.task.draft_task_id} has {scheduled_minutes} "
                        f"scheduled minutes but its estimate is "
                        f"{draft.task.estimated_minutes} minutes."
                    ),
                    draft_task_id=draft.task.draft_task_id,
                )
            )
    # sort by start time of the sessions to check for overlaps and insufficient buffer
    all_sessions.sort(key=lambda item: item[1].start_at)
    required_buffer = timedelta(
        minutes=constraints.buffer_minutes
    )  # get the buffer time required between sessions
    # _ don't care previous is the previous session is a tuple, task_id and current is the current session in the sorted list of all sessions
    # also zip the list of all sessions with itself but shifted by one to get pairs of previous and current sessions
    # example (task1, session1), (task2, session2)
    # example of zip ((9->10), (10->11))
    for (_, previous), (task_id, current) in zip(all_sessions, all_sessions[1:]):
        # check if the current session starts before the previous session ends, indicating an overlap
        if current.start_at < previous.end_at:
            notes.append(
                ValidationNote(
                    code="overlap",
                    message=(
                        f"{current.draft_session_id} starts at "
                        f"{current.start_at.isoformat()} before "
                        f"{previous.draft_session_id} ends at "
                        f"{previous.end_at.isoformat()}."
                    ),
                    draft_task_id=task_id,
                    draft_session_id=current.draft_session_id,
                    related_session_id=previous.draft_session_id,
                )
            )
        # check if the current session starts before the required buffer time after the previous session ends, indicating insufficient buffer
        elif current.start_at < previous.end_at + required_buffer:
            required_start = previous.end_at + required_buffer
            notes.append(
                ValidationNote(
                    code="insufficient_buffer",
                    message=(
                        f"{current.draft_session_id} starts at "
                        f"{current.start_at.isoformat()}, but it must start at or "
                        f"after {required_start.isoformat()} to preserve the "
                        f"{constraints.buffer_minutes}-minute buffer after "
                        f"{previous.draft_session_id}."
                    ),
                    draft_task_id=task_id,
                    draft_session_id=current.draft_session_id,
                    related_session_id=previous.draft_session_id,
                )
            )
    # if there are validation notes and the schedule has been revised 3 or more times, raise an error with the messages of the notes
    if notes and revision_count >= 3:
        messages = "\n".join(note.message for note in notes)
        raise ValueError(
            f"Draft schedule still has validation errors after three revisions:\n{messages}"
        )

    return {
        "validation_notes": notes,
        "schedule_revision_count": revision_count,
    }


async def revise_draft_schedule(
    state: AgentState,
    model,
):
    """Revise the draft schedule from validation notes or user feedback."""

    validation_notes = state.get("validation_notes") or []
    user_feedback = state.get("user_revision_request")
    has_validation_notes = bool(validation_notes)
    has_user_feedback = bool(user_feedback and user_feedback.strip())

    if has_validation_notes == has_user_feedback:
        raise ValueError(
            "Exactly one of validation_notes or user_revision_request is required"
        )

    revision_count = state.get("schedule_revision_count", 0)
    if has_validation_notes and revision_count >= 3:
        raise ValueError("Draft schedule has already been revised three times")

    draft_schedule = state["draft_schedule"]

    if not draft_schedule.drafts:
        raise ValueError("Draft schedule is empty, cannot revise")

    planning_constraints = state["planning_constraints"]
    if not planning_constraints.daily_periods:
        raise ValueError(
            "No available periods in planning constraints, cannot revise draft schedule"
        )

    subjects = state["subjects"]
    if not subjects:
        raise ValueError("No subjects available, cannot revise draft schedule")

    user_request = get_latest_user_request(state)
    if has_validation_notes:
        system_message = SystemMessage(
            content=REVISE_DRAFT_SCHEDULE_PROMPT.format(
                user_request=user_request,
                subjects=json.dumps(
                    [subject.model_dump(mode="json") for subject in subjects], indent=2
                ),
                draft_schedule=draft_schedule.model_dump_json(indent=2),
                validation_notes=json.dumps(
                    [note.model_dump(mode="json") for note in validation_notes], indent=2
                ),
                planning_constraints=planning_constraints.model_dump_json(indent=2),
            )
        )
        next_revision_count = revision_count + 1
    else:
        system_message = SystemMessage(
            content=REVISE_FROM_USER_FEEDBACK_PROMPT.format(
                user_request=user_request,
                user_feedback=user_feedback,
                draft_schedule=draft_schedule.model_dump_json(indent=2),
                planning_constraints=planning_constraints.model_dump_json(indent=2),
                subjects=json.dumps(
                    [subject.model_dump(mode="json") for subject in subjects], indent=2
                ),
            )
        )
        next_revision_count = revision_count

    messages = [system_message]
    for attempt in range(3):
        response = await model.ainvoke(messages)
        if response["parsing_error"] is None and response["parsed"] is not None:
            return {
                "draft_schedule": response["parsed"],
                "schedule_revision_count": next_revision_count,
                "validation_notes": [],
                "user_revision_request": None,
            }

        if attempt < 2:
            messages = [
                system_message,
                response["raw"],
                HumanMessage(
                    content=(
                        f"Validation failed:\n{response['parsing_error']}\n"
                        "Correct the errors and return the complete DraftSchedule."
                    )
                ),
            ]

    raise ValueError("Draft revision failed after three attempts")


def review_schedule(
    state: AgentState,
) -> Command[
    Literal["create_schedule", "revise_draft_schedule", "__end__"]
]:
    """Pause for draft review, then route the user's decision."""
    decision = interrupt(
        {
            "type": "schedule_review",
            "title": "Review your study schedule",
            "draft": state["draft_schedule"].model_dump(mode="json"),
            "options": [
                {
                    "value": "approve",
                    "label": "Approve schedule",
                    "variant": "success",
                    "requires_feedback": False,
                },
                {
                    "value": "edit",
                    "label": "Request changes",
                    "variant": "secondary",
                    "requires_feedback": True,
                    "feedback": {
                        "label": "What would you like to change?",
                        "placeholder": "Move Monday's session to Tuesday...",
                        "min_length": 1,
                    },
                },
                {
                    "value": "cancel",
                    "label": "Cancel",
                    "variant": "danger",
                    "requires_feedback": False,
                    "requires_confirmation": True,
                    "confirmation_message": "Discard this draft schedule?",
                },
            ],
        }
    )

    if not isinstance(decision, dict):
        raise ValueError("Schedule review decision must be an object")

    action = decision.get("action")

    if action == "approve":
        return Command(goto="create_schedule")

    if action == "edit":
        feedback = decision.get("feedback")
        if not isinstance(feedback, str) or not feedback.strip():
            raise ValueError("Feedback is required for 'edit' action")
        return Command(
            update={"user_revision_request": feedback.strip()},
            goto="revise_draft_schedule",
        )

    if action == "cancel":
        return Command(goto=END)

    raise ValueError(f"Unknown review action: {action}")


async def create_schedule(
    state: AgentState,
    runtime: Runtime[RequestContext],
) -> dict[str, ScheduleResponse]:
    """Persist the approved draft schedule through the StudyOps API."""

    draft_schedule = state.get("draft_schedule")
    if draft_schedule is None or not draft_schedule.drafts:
        raise ValueError("Cannot create a schedule without an approved draft")

    settings = Config()
    async with StudyOpsAPIClient(
        settings.base_drf_api,
        access_token=runtime.context.access_token,
        refresh_token=runtime.context.refresh_token,
    ) as client:
        schedule = await client.create_draft_schedule(draft_schedule)

    return {"schedule": schedule}


async def summary_workflow(
    state: AgentState,
    runtime: Runtime[RequestContext],
    model,
):
    """Summarize the API-confirmed schedule and append the final message."""
    schedule = state.get("schedule")
    if schedule is None:
        raise ValueError("Cannot summarize a schedule that has not been created")

    timezone_name, _ = _user_timezone(runtime.context.timezone)
    system_message = FINAL_SUMMARY_PROMPT.format(
        schedule=schedule.model_dump_json(indent=2),
        timezone=timezone_name,
    )

    response = await model.ainvoke([SystemMessage(content=system_message)])
    return {"messages": [response], "schedule": schedule}
