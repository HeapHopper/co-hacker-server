from langgraph.graph import StateGraph
from pydantic import BaseModel
from langsmith import traceable

from code_analysis.code_analysis_models import SnippetInput, CodeSnippet
from code_analysis.code_analysis_prompt_chain import code_analysis_chain

# LangGraph-compatible state
class CodeAnalysisGraphState(BaseModel):
    input: SnippetInput
    output: CodeSnippet | None = None

# Single-node LangGraph
@traceable(name="analyze_snippet", description="Analyze code snippet for vulnerabilities")
def analyze_node(state: CodeAnalysisGraphState) -> dict:
    result = code_analysis_chain.invoke({"snippet": state.input.snippet})
    return {"output": result}

def build_code_analysis_graph():
    builder = StateGraph(CodeAnalysisGraphState)
    builder.add_node("analyze", analyze_node)
    builder.set_entry_point("analyze")
    builder.set_finish_point("analyze")
    return builder.compile()
