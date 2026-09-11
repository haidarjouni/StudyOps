from langgraph.graph import MessagesState

from schemas import (DraftSchedule, PlanningConstraints, PlanningSubject,
                     ResolvedPlanningRequest, ValidationNote)


class AgentState(MessagesState):
    """Conversation state for the StudyOps assistant."""

    planning_request: ResolvedPlanningRequest
    planning_constraints: PlanningConstraints
    draft_schedule: DraftSchedule
    subjects: list[PlanningSubject]
    validation_notes: list[ValidationNote]
    schedule_revision_count: int
    user_revision_request: str | None