import asyncio
from functools import partial

from langchain.messages import HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from config import Config
from nodes import call_model
from runtime_context import RequestContext
from state import AgentState
from tools import READ_TOOLS
from local_testing import get_demo_context


config = Config()

model = ChatOllama(
    model="qwen3.5:9b",
    temperature=0,
    base_url=config.ollama_url,
)  # create the model

model_with_tools = model.bind_tools(READ_TOOLS)

assistant_node = partial(call_model, model=model_with_tools)

graph = StateGraph(AgentState, context_schema=RequestContext)
graph.add_node("assistant", assistant_node)
graph.add_node("tools", ToolNode(READ_TOOLS))
graph.add_edge(START, "assistant")
graph.add_conditional_edges("assistant", tools_condition)
graph.add_edge("tools", "assistant")

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

    print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
