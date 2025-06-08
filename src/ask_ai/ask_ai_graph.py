from langgraph.graph import StateGraph
from pydantic import BaseModel
from langsmith import traceable

from ask_ai.ask_ai_models import AskAiRequest, AskAiResponse
from ask_ai.ask_ai_prompt_chain import ask_ai_chain

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