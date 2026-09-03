from langgraph.graph import MessagesState

from schemas import PlanningConstraints, ResolvedPlanningRequest


class AgentState(MessagesState):
    """Conversation state for the StudyOps assistant."""

    planning_request: ResolvedPlanningRequest
    planning_constraints: PlanningConstraints
