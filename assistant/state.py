from langgraph.graph import MessagesState

from assistant.schemas.draft_schedule import DraftSchedule
from schemas import PlanningConstraints, ResolvedPlanningRequest


class AgentState(MessagesState):
    """Conversation state for the StudyOps assistant."""

    planning_request: ResolvedPlanningRequest
    planning_constraints: PlanningConstraints
    draft_schedule: DraftSchedule