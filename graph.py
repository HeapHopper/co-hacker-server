from langgraph.graph import StateGraph
from pydantic import BaseModel
from models import SnippetInput, CodeSnippet
from prompt_chain import chain

# LangGraph-compatible state
class GraphState(BaseModel):
    input: SnippetInput
    output: CodeSnippet | None = None

# Single-node LangGraph
def analyze_node(state: GraphState) -> dict:
    result = chain.invoke({"snippet": state.input.snippet})
    return {"output": result}

def build_graph():
    builder = StateGraph(GraphState)
    builder.add_node("analyze", analyze_node)
    builder.set_entry_point("analyze")
    builder.set_finish_point("analyze")
    return builder.compile()
