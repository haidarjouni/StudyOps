from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from langchain.messages import SystemMessage
from langgraph.runtime import Runtime

from prompts import CONTEXT_RETRIEVAL_PROMPT
from runtime_context import RequestContext
from state import AgentState


async def retrieve_context(
    state: AgentState,
    runtime: Runtime[RequestContext],
    model,
):
    """Retrieve the tool-backed context required by the planning workflow."""

    timezone_name = runtime.context.timezone
    try:
        user_timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone_name = "UTC"
        user_timezone = ZoneInfo(timezone_name)

    system_message = SystemMessage(
        content=CONTEXT_RETRIEVAL_PROMPT.format(
            current_datetime=datetime.now(user_timezone).isoformat(),
            timezone=timezone_name,
        )
    )

    response = await model.ainvoke([system_message, *state["messages"]])
    return {"messages": [response]}
