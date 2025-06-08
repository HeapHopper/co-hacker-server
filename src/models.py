from pydantic import BaseModel

### AI Models for Code Snippet Analysis

class SnippetInput(BaseModel):
    snippet: str

class CodeSnippet(BaseModel):
    is_vulnerable: bool
    vulnerability_type: str
    vulnerability: str
    suggest_fix: str


mock_safe_snippet = CodeSnippet(
            is_vulnerable="False",
            vulnerability_type="",
            vulnerability="",
            suggest_fix=""
        )

mock_vulnerable_snippet = CodeSnippet(
            is_vulnerable="True",
            vulnerability_type="test vulnerability",
            vulnerability="this is a test vulnerability",
            suggest_fix="/* This is a test fix */\n"
        )

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
