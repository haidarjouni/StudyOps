from dataclasses import dataclass
import operator
from typing import Annotated, Any
from langgraph.graph import MessagesState
from typing import Literal
from pydantic import BaseModel

@dataclass
class RequestContext:
    access_token: str | None
    refresh_token: str | None

class ContextRequest(BaseModel):
    source: Literal["tasks", "sessions", "preferences", "subjects"]
    reason: str

class ContextCheckOutput(BaseModel):
    context_needed: list[ContextRequest]
    
class AgentState(MessagesState):
    context_needed: list[ContextRequest]
    context: Annotated[list[dict[str, Any]], operator.add] # operator.add is used to merge lists of context from multiple messages into a single list
    errors: Annotated[list[str], operator.add] # operator.add is used to merge lists of errors from multiple messages into a single list
