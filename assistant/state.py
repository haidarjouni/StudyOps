from langgraph.graph import MessagesState

from schemas import (DraftSchedule, PlanningConstraints, PlanningSubject,
                     ResolvedPlanningRequest)


class AgentState(MessagesState):
    """Conversation state for the StudyOps assistant."""

    planning_request: ResolvedPlanningRequest
    planning_constraints: PlanningConstraints
    draft_schedule: DraftSchedule
    subjects: list[PlanningSubject]
