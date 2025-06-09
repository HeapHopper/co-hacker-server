from pydantic import BaseModel

### AI Request and Response Models

class AskAiRequest(BaseModel):
    snippet: str

class AskAiResponse(BaseModel):
    answer: str

mock_ai_request = AskAiRequest(
    snippet="    if (x = y) {        return -1;    }"
)

mock_ai_response = AskAiResponse(
    answer="""
The code has an issue: the condition uses assignment = instead of comparison ==. This causes x to be assigned the value of y, and the condition will be true whenever y is non-zero.

Fix:

if (x == y) {
    return -1;
}
"""
)
