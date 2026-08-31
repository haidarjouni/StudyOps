from typing import Any

from context import AgentState, ContextRequest 
from prompts import CONTEXT_CHECKER_SYSTEM_PROMPT
from langchain.messages import SystemMessage

async def get_context_needed(state: AgentState, context_checker) -> dict[str, list[ContextRequest]]:
    system_prompt = SystemMessage( #create system message
        content=CONTEXT_CHECKER_SYSTEM_PROMPT.format( # get the content of the system prompt and insert the current context stored in state into the prompt
            context=state.get("context", []) 
        )
    )
    
    result = await context_checker.ainvoke([
        system_prompt, # Provide the system prompt to the context checker
        *state["messages"] # provide the rest of the messages in the conversation to the context checker
    ])
    
    return{
        "context_needed": result.context_needed # return a structured output of the context needed by the agent, which is a list of ContextRequest objects
    }