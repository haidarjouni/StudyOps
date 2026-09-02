import asyncio
from functools import partial

from langchain.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph

from config import Config
from nodes import get_context_needed
from runtime_context import RequestContext
from schemas.context_requests import ContextCheckOutput
from state import AgentState

config = Config()


def route_context_requests(state: AgentState) -> list[str]:
    return list(state.context_needed.keys()) or [
        END
    ]  # return a list of the context sources needed by the agent, which is a list of strings. This is used to determine which nodes to route to next based on the context needed by the agent.


model = ChatOllama(
    model="qwen3.5:9b",
    temperature=0,
)  # create the model

context_checker = model.with_structured_output(
    ContextCheckOutput
)  # create output parser

get_context_needed_node = partial(
    get_context_needed,
    context_checker=context_checker,
)  # since langgraph automatically passes the state to the node function, we can use partial to pass in the context_checker as a fixed argument to the get_context_needed function. This allows us to create a node that only requires the state as input, while still having access to the context_checker.

graph = StateGraph(AgentState, context_schema=RequestContext)
graph.add_node("check_context_needed", get_context_needed_node)  # create the node
graph.add_edge(
    START, "check_context_needed"
)  # add an edge from the start node to the check_context_needed node
graph.add_edge(
    "check_context_needed", END
)  # add an edge from the check_context_needed node to the route_context_requests function, which will determine the next node based on the context needed by the agent

app = graph.compile()  # compile the graph into an app that can be run


async def main():
    result = await app.ainvoke(
        {
            "messages": [
                HumanMessage(
                    content="I have a Data Structures exam coming up next week, and I need help creating a study plan. Can you assist me with that?"
                )
            ],
            "context_needed": [],
            "context": [],
            "errors": [],
        },
        context=RequestContext(
            access_token=None,
            refresh_token=None,
            timezone="Asia/Beirut",
        ),
    )

    print(result["context_needed"])


if __name__ == "__main__":
    asyncio.run(main())
