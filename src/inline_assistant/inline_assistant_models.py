from pydantic import BaseModel

class Vulnerability(BaseModel):
    description: str
    vulnerable_code: str

### AI Models for Code Snippet Analysis

class InlineAssistantRequest(BaseModel):
    current_line: str
    current_scope: str
    current_file: str

class InlineAssistantResponse(BaseModel):
    is_vulnerable: bool
    vulnerability: Vulnerability | None = None
    suggest_fix: str

#TODO add support for multiple vulnerabilities
