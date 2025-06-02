from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import SnippetInput, CodeSnippet, mock_vulnerable_snippet
from graph import build_graph, GraphState

import uvicorn
import os
from langsmith import traceable

app = FastAPI()

# Optional CORS for local dev or VSCode extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Build LangGraph
graph = build_graph()

@app.post("/analyze", response_model=CodeSnippet)
async def analyze_snippet(input: SnippetInput):
    try:
        result_state = graph.invoke(GraphState(input=input))
        print()
        # return result_state.output
        return result_state['output']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":

    # Optional: confirm that LangSmith is active
    if not os.getenv("LANGSMITH_API_KEY"):
        print("⚠️ LangSmith tracing disabled (no API key set).")
    else:
        print("✅ LangSmith tracing enabled.")


    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
