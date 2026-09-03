from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from langchain.messages import SystemMessage
from langgraph.runtime import Runtime

from prompts import CONTEXT_RETRIEVAL_PROMPT, RESOLVE_PLANNING_REQUEST_PROMPT
from runtime_context import RequestContext
from schemas import RetrievedContext
from state import AgentState


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
