import json
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from langchain.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.runtime import Runtime

from planning import build_planning_constraints
from prompts import (CONTEXT_RETRIEVAL_PROMPT, GENERATE_DRAFT_SCHEDULE_PROMPT,
                     RESOLVE_PLANNING_REQUEST_PROMPT)
from runtime_context import RequestContext
from schemas import PlanningSubject, StudyPreference
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
    for i in range(3): # for retry
        response = await model.ainvoke(messages) # run first time
        #parsing error is none if successful parsing, parsed is the parsed draft schedule
        if response["parsing_error"] is None and response["parsed"] is not None: # if successful parsing
            return {"draft_schedule": response["parsed"]}
           
        if i < 2:
            # if failed  add the system message the raw response and human message that specifies the validation error and asks for correction
            messages = [
                system_message,
                response["raw"], # Message containing the invalid draft
                HumanMessage(
                    content=(
                        f"Validation failed:\n{response['parsing_error']}\n"
                        "Correct the errors and return the complete DraftSchedule."
                    )
                ),
            ] 
    # if failed 3 times raise error
    raise ValueError("Draft generation failed after three attempts")
