import asyncio
from functools import partial

from langchain.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph import END, START, StateGraph

from config import Config
from context import AgentState, ContextCheckOutput
from nodes import get_context_needed

config = Config()

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

graph = StateGraph(AgentState)
graph.add_node("check_context_needed", get_context_needed_node)  # create the node
graph.add_edge(START, "check_context_needed")  # link from start till that node
graph.add_edge("check_context_needed", END)  # till that node to end

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
        }
    )

    print(result["context_needed"])


asyncio.run(main())
