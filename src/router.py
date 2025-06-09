from fastapi import APIRouter

from code_analysis.code_analysis_route import router as code_analysis_router
from ask_ai.ask_ai_route import router as ask_ai_router

# Create the main API router
router = APIRouter()

# Include the code analysis and ask AI routers
router.include_router(code_analysis_router)
router.include_router(ask_ai_router)