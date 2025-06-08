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