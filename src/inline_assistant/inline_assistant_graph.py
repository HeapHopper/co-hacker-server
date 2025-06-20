from langgraph.graph import StateGraph
from pydantic import BaseModel
from langsmith import traceable

from inline_assistant.inline_assistant_models import InlineAssistantRequest, InlineAssistantResponse
from inline_assistant.inline_assistant_prompt_chain import inline_assistant_chain

# LangGraph-compatible state
class InlineAssistantGraphState(BaseModel):
    input: InlineAssistantRequest
    output: InlineAssistantResponse | None = None  

# Single-node LangGraph
@traceable(name="inline_assistant", description="Inline code assistant for C/C++ vulnerabilities")
def inline_assistant_node(state: InlineAssistantGraphState) -> dict:
    result = inline_assistant_chain.invoke({
        "line": state.input.current_line,
        "scope": state.input.current_scope,
        "file": state.input.current_file
    })
    return {"output": result}

def build_inline_assistant_graph():
    builder = StateGraph(InlineAssistantGraphState)
    builder.add_node("inline_assistant", inline_assistant_node)
    builder.set_entry_point("inline_assistant")
    builder.set_finish_point("inline_assistant")
    return builder.compile()

