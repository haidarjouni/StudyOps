from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from langchain.messages import SystemMessage
from langgraph.runtime import Runtime

from prompts import CONTEXT_CHECKER_PROMPT
from runtime_context import RequestContext
from schemas.context_requests import ContextRequest
from state import AgentState


async def get_context_needed(
    state: AgentState,
    runtime: Runtime[RequestContext],
    context_checker,
) -> dict[str, list[ContextRequest]]:
    timezone_name = runtime.context.timezone # so before we can use the timezone, we need to get it from the runtime context. The runtime context is a RequestContext object that contains the user's timezone, which is used to resolve relative dates into explicit timezone-aware timestamps.
    try:
        user_timezone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        timezone_name = "UTC"
        user_timezone = ZoneInfo(timezone_name)

    current_datetime = datetime.now(user_timezone).isoformat() # get the current date and time in the user's timezone and convert it to an ISO 8601 string. This is used to provide the context checker with the current date and time, which is necessary for resolving relative dates into explicit timestamps.
    system_prompt = SystemMessage(  # create system message
        content=CONTEXT_CHECKER_PROMPT.format(  # get the content of the system prompt and insert the current context stored in state into the prompt
            context=state.get("context", []),
            current_datetime=current_datetime,
            timezone=timezone_name,
        )
    )

    result = await context_checker.ainvoke(
        [
            system_prompt,  # Provide the system prompt to the context checker
            *state[
                "messages"
            ],  # provide the rest of the messages in the conversation to the context checker
        ]
    )

    return {
        "context_needed": result.context_needed  # return a structured output of the context needed by the agent, which is a list of ContextRequest objects
    }
