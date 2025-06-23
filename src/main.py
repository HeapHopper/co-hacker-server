# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Import fastapi libraries
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import the main router
from router import router as main_router

import uvicorn
import os

app = FastAPI()

# Optional CORS for local dev or VSCode extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the main router
app.include_router(main_router)


@app.get("/")
def read_root():
    return {"message": "Hello from Railway!"}

if __name__ == "__main__":

    # Optional: confirm that LangSmith is active
    if not os.getenv("LANGSMITH_API_KEY"):
        print("LangSmith tracing disabled (no API key set).")
    else:
        print("LangSmith tracing enabled.")


    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
