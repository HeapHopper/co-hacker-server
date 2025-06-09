from fastapi import APIRouter, HTTPException
from .ask_ai_models import AskAiRequest, AskAiResponse
from .ask_ai_graph import build_ask_ai_graph, AskAiGraphState

router = APIRouter(prefix="/ask_ai", tags=["ask_ai"])

ask_ai_graph = build_ask_ai_graph()

@router.post("/", response_model=AskAiResponse)
async def ask_ai(input: AskAiRequest):
    try:
        result_state = ask_ai_graph.invoke(AskAiGraphState(input=input))
        return result_state['output']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))