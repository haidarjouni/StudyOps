import asyncio
from functools import partial
from typing import Literal

from langchain.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from config import Config
from local_testing import get_demo_context
from nodes import (collect_constraints, resolve_planning_request,
                   retrieve_context)
from runtime_context import RequestContext
from schemas import ResolvedPlanningRequest
from state import AgentState
from tools import READ_TOOLS

config = Config()

model = ChatOllama(
    model="qwen3.5:9b",
    temperature=0,
    base_url=config.ollama_url,
)  # create the model

model_with_tools = model.bind_tools(READ_TOOLS)
planning_request_model = model.with_structured_output(ResolvedPlanningRequest)

resolve_planning_request_node = partial(
    resolve_planning_request,
    model=planning_request_model,
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


graph = StateGraph(AgentState, context_schema=RequestContext)
graph.add_node("resolve_planning_request", resolve_planning_request_node)
graph.add_node("retrieve_context", retrieve_context_node)
graph.add_node("tools", ToolNode(READ_TOOLS))
graph.add_node("collect_constraints", collect_constraints)
graph.add_edge(START, "resolve_planning_request")
graph.add_edge("resolve_planning_request", "retrieve_context")
graph.add_conditional_edges("retrieve_context", route_after_context_retrieval)
graph.add_edge("tools", "retrieve_context")
graph.add_edge("collect_constraints", END)

app = graph.compile()  # compile the graph into an app that can be run

# print(app.get_graph().draw_mermaid())


async def main():
    request_context = await get_demo_context()
    result = await app.ainvoke(
        {
            "messages": [
                HumanMessage(
                    content="Create a study plan for my upcoming tasks over the next seven days."
                )
            ],
        },
        context=request_context,
    )

    print(result["planning_constraints"].model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
