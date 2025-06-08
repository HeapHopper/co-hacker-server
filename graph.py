from langgraph.graph import StateGraph
from pydantic import BaseModel
from models import SnippetInput, CodeSnippet, AskAiRequest, AskAiResponse
from prompt_chain import code_analysis_chain, ask_ai_chain
from langsmith import traceable

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


class AskAiGraphState(BaseModel):
    input: AskAiRequest
    output: AskAiResponse | None = None

@traceable(name="ask_ai", description="Ask AI for code analysis")
def ask_ai_node(state: AskAiGraphState) -> dict:
    result = ask_ai_chain.invoke({"snippet": state.input.snippet})
    return {"output": result}

def build_ask_ai_graph():
    builder = StateGraph(AskAiGraphState)
    builder.add_node("ask_ai", ask_ai_node)
    builder.set_entry_point("ask_ai")
    builder.set_finish_point("ask_ai")
    return builder.compile()
