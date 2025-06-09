from fastapi import APIRouter, HTTPException

from .code_analysis_models import SnippetInput, CodeSnippet
from .code_analysis_graph import build_code_analysis_graph, CodeAnalysisGraphState

router = APIRouter(prefix="/analyze", tags=["code_analysis"])

code_analysis_graph = build_code_analysis_graph()

@router.post("/", response_model=CodeSnippet)
async def analyze_snippet(input: SnippetInput):
    try:
        result_state = code_analysis_graph.invoke(CodeAnalysisGraphState(input=input))
        return result_state['output']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))