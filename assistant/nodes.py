from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from langchain.messages import SystemMessage
from langgraph.runtime import Runtime

from prompts import ASSISTANT_PROMPT
from runtime_context import RequestContext
from state import AgentState


async def call_model(
    state: AgentState,
    runtime: Runtime[RequestContext],
    model,
):
    """Call the assistant model with the conversation and bound tools."""

    timezone_name = runtime.context.timezone
    try:
        user_timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone_name = "UTC"
        user_timezone = ZoneInfo(timezone_name)

    system_message = SystemMessage(
        content=ASSISTANT_PROMPT.format(
            current_datetime=datetime.now(user_timezone).isoformat(),
            timezone=timezone_name,
        )
    )

    response = await model.ainvoke([system_message, *state["messages"]])
    return {"messages": [response]}
