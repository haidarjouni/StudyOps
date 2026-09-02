import operator
from typing import Annotated, Any

from langgraph.graph import MessagesState

from schemas.context_requests import ContextRequest, ContextSource


class AgentState(MessagesState):
    """State shared by nodes while processing an assistant request."""

    # List of context requests that the agent needs.
    context_needed: dict[ContextSource, ContextRequest]

    # List of context information from the tools.
    context: Annotated[
        list[dict[str, Any]], operator.add
    ]  # operator.add merges context lists from multiple messages into one list.

    errors: Annotated[
        list[str], operator.add
    ]  # operator.add merges error lists from multiple messages into one list.
