from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama
from nodes import get_context_needed
from context import AgentState, ContextCheckOutput 
from functools import partial

model = ChatOllama(
    model="qwen3.5:4b",
    temperature=0,
) #create the model

context_checker = model.with_structured_output(
    ContextCheckOutput
) #create output parser

get_context_needed_node = partial(
    get_context_needed,
    context_checker=context_checker,
) # since langgraph automatically passes the state to the node function, we can use partial to pass in the context_checker as a fixed argument to the get_context_needed function. This allows us to create a node that only requires the state as input, while still having access to the context_checker.

graph = StateGraph(AgentState)
graph.add_node("check_context_needed", get_context_needed_node) #create the node
graph.add_edge(START, "check_context_needed") #link from start till that node
graph.add_edge("check_context_needed", END) # till that node to end

app = graph.compile() # compile the graph into an app that can be run


