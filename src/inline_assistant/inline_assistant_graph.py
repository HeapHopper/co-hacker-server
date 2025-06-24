from typing import Literal
from langgraph.graph import StateGraph
from pydantic import BaseModel
from langsmith import traceable

from inline_assistant.inline_assistant_models import InlineAssistantRequest, InlineAssistantResponse
from inline_assistant.inline_assistant_prompt_chain import initial_classifier_chain, vulnerability_chain, scope_check_chain, file_check_chain, std_upgrade_chain

class InlineAssistantGraphState(BaseModel):
    input: InlineAssistantRequest
    output: InlineAssistantResponse | None = None
    confidence_level: float | None = None
    unsafe_pattern_detected: bool = False
    suggestion_type: Literal["std_upgrade", "vulnerable", "safe", "scope_check", "file_check"] | None = None


@traceable(name="initial_classifier")
def initial_classifier_node(state: InlineAssistantGraphState) -> dict:
        
    result = initial_classifier_chain.invoke({
        "line": state.input.current_line
    })
    state.confidence_level = result.confidence_level
    state.unsafe_pattern_detected = result.unsafe_pattern_detected
    state.suggestion_type = result.suggestion_type
    return state.dict()

@traceable(name="handle_safe")
def handle_safe_node(state: InlineAssistantGraphState) -> dict:
    state.output = InlineAssistantResponse(
        is_vulnerable=False,
        vulnerability=None,
        suggest_fix=""
    )
    return state.dict()

@traceable(name="handle_vulnerable")
def handle_vulnerable_node(state: InlineAssistantGraphState) -> dict:
    state.output = vulnerability_chain.invoke({
        "line": state.input.current_line,
        "scope": state.input.current_scope
    })
    return state.dict()

@traceable(name="check_scope")
def check_scope_node(state: InlineAssistantGraphState) -> dict:
    result = scope_check_chain.invoke({
        "line": state.input.current_line,
        "scope": state.input.current_scope
    })
    state.confidence_level = result["confidence_level"]
    state.suggestion_type = result["suggestion_type"]
    return state.dict()

@traceable(name="check_file")
def check_file_node(state: InlineAssistantGraphState) -> dict:
    result = file_check_chain.invoke({
        "line": state.input.current_line,
        "scope": state.input.current_file,
        "file": state.input.current_file
    })
    state.suggestion_type = result["suggestion_type"]
    return state.dict()

@traceable(name="suggest_std_upgrade")
def suggest_std_upgrade_node(state: InlineAssistantGraphState) -> dict:
    state.output = std_upgrade_chain.invoke({
        "line": state.input.current_line
    })
    return state.dict()

def build_inline_assistant_graph():
    builder = StateGraph(InlineAssistantGraphState)
    
    builder.add_node("initial_classifier", initial_classifier_node)
    builder.add_node("handle_safe", handle_safe_node)
    builder.add_node("handle_vulnerable", handle_vulnerable_node)
    builder.add_node("check_scope", check_scope_node)
    builder.add_node("check_file", check_file_node)
    builder.add_node("suggest_std_upgrade", suggest_std_upgrade_node)

    builder.add_conditional_edges(
        "initial_classifier",
        lambda state: (
            "handle_safe" if state.confidence_level >= 0.9 else
            "handle_vulnerable" if state.unsafe_pattern_detected else
            "check_scope" if state.suggestion_type == "scope_check" else
            "suggest_std_upgrade" if state.suggestion_type == "std_upgrade" else
            "check_scope"  # fallback
        )    
    )

    builder.add_conditional_edges(
        "check_scope",
        lambda state: (
            "handle_vulnerable" if state.suggestion_type == "vulnerable" else
            "handle_safe" if state.confidence_level >= 0.66 else
            "suggest_std_upgrade" if state.suggestion_type == "std_upgrade" else
            "check_file"
        )
    )

    builder.add_conditional_edges(
        "check_file",
        lambda state: (
            "handle_vulnerable" if state.suggestion_type == "vulnerable" else
            "handle_safe"
        )
    )

    builder.set_entry_point("initial_classifier")

    builder.set_finish_point("handle_safe")
    builder.set_finish_point("handle_vulnerable")
    builder.set_finish_point("suggest_std_upgrade")
    
    return builder.compile()

