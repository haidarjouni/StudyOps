import argparse
import asyncio
from functools import partial
from typing import Literal

from langchain.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from config import Config
from local_testing import get_demo_context
from nodes import (collect_constraints, generate_draft_schedule,
                   resolve_planning_request, retrieve_context,
                   revise_draft_schedule, validate_schedule)
from runtime_context import RequestContext
from schemas import DraftSchedule, ResolvedPlanningRequest
from state import AgentState
from tools import READ_TOOLS

config = Config()

model = ChatOpenAI(
    model=config.openai_model,
    reasoning_effort="low",
)  # create the model

# Terra requires reasoning disabled for function tools on Chat Completions.
model_with_tools = model.bind_tools(READ_TOOLS, reasoning_effort="none")
planning_request_model = model.with_structured_output(
    ResolvedPlanningRequest,
    method="json_schema",  # specify the method for structured output
    strict=True,  # enforce strict validation of the output
)
draft_schedule_model = model.with_structured_output(
    DraftSchedule,  # the pydantic model to validate against
    method="json_schema",  # specify the method for structured output
    strict=True,  # enforce strict validation of the output
    include_raw=True,  # include the raw output from the model in the result
)

resolve_planning_request_node = partial(
    resolve_planning_request,
    model=planning_request_model,
)
generate_draft_schedule_node = partial(
    generate_draft_schedule,
    model=draft_schedule_model,
)
revise_draft_schedule_node = partial(
    revise_draft_schedule,
    model=draft_schedule_model,
)

retrieve_context_node = partial(retrieve_context, model=model_with_tools)


def route_after_context_retrieval(
    state: AgentState,
) -> Literal["tools", "collect_constraints"]:
    """Run requested tools, or continue once retrieval is complete."""

    if getattr(
        state["messages"][-1], "tool_calls", None
    ):  # checks if the last message has any tool calls
        return "tools"
    return "collect_constraints"


def route_after_validation(
    state: AgentState,
) -> Literal["revise_draft_schedule", END]:  # type: ignore
    """Revise invalid schedules and finish when validation succeeds."""
    if state["validation_notes"]:
        return "revise_draft_schedule"
    return END


graph = StateGraph(AgentState, context_schema=RequestContext)
graph.add_node("resolve_planning_request", resolve_planning_request_node)
graph.add_node("retrieve_context", retrieve_context_node)
graph.add_node("tools", ToolNode(READ_TOOLS))
graph.add_node("collect_constraints", collect_constraints)
graph.add_node("generate_draft_schedule", generate_draft_schedule_node)
graph.add_node("validate_schedule", validate_schedule)
graph.add_node("revise_draft_schedule", revise_draft_schedule_node)
graph.add_edge(START, "resolve_planning_request")
graph.add_edge("resolve_planning_request", "retrieve_context")
graph.add_conditional_edges("retrieve_context", route_after_context_retrieval)
graph.add_edge("tools", "retrieve_context")
graph.add_edge("collect_constraints", "generate_draft_schedule")
graph.add_edge("generate_draft_schedule", "validate_schedule")
graph.add_conditional_edges("validate_schedule", route_after_validation)
graph.add_edge("revise_draft_schedule", "validate_schedule")

# print(app.get_graph().draw_mermaid())


async def main(thread_id):
    async with AsyncPostgresSaver.from_conn_string(
        config.checkpoint_database_url
    ) as checkpointer:
        app = graph.compile(checkpointer=checkpointer)
        snapshot = await app.aget_state({"configurable": {"thread_id": str(thread_id)}})

        print(snapshot.values)


if __name__ == "__main__":
    asyncio.run(main(thread_id="50eb8fe8-572b-464c-afab-b68de691b817"))
