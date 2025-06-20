from fastapi import APIRouter, HTTPException

from .inline_assistant_models import InlineAssistantRequest, InlineAssistantResponse
from .inline_assistant_graph import build_inline_assistant_graph, InlineAssistantGraphState

router = APIRouter(prefix="/inline_assistant", tags=["inline_assistant"])

inline_assistant_graph = build_inline_assistant_graph()

@router.post("/", response_model=InlineAssistantResponse)
async def inline_assistant(input: InlineAssistantRequest):
    try:
        result_state = inline_assistant_graph.invoke(InlineAssistantGraphState(input=input))
        return result_state['output']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
