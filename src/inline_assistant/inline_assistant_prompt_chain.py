from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable
from config import OPENAI_API_KEY

from inline_assistant.inline_assistant_models import InlineAssistantResponse

### INLINE ASSISTANT LANGCHAIN

inline_assistant_llm = ChatOpenAI(
    model='gpt-4.1-nano',
    api_key=OPENAI_API_KEY
)

INLINE_ASSISTANT_USER_PROMPT = HumanMessagePromptTemplate.from_template("""
You are a C/C++ inline code assistant that provides concise, actionable suggestions - focusing on vulnerability detection and secure code.
You will be given the current line of code, its scope, and the file name. Your task is to analyze the code and provide a structured response.
                                                                        
start with analyzing the current line of code:
```{line}```
                                                                        
The current scope is also provided for context, use it to understand the context of the code when:
  - the current line is suspicious and extra context is needed to decide if it is vulnerable or not
  - memory allocation or deallocation is involved, as vulnerabilities can arise from using the allocator or deallocator incorrectly in the scope
```{scope}```
                                                                                                                       
The output should focus on security issues in the current line, using the scope as merely context.
The output should include:
- is_vulnerable: true or false
- vulnerability:
    - description: a brief description of the vulnerability
    - vulnerable_code: the specific code that is vulnerable
                                                                        
- suggest_fix: ONLY the fixed C/C++ code that addresses the vulnerability.
  - The fix must be a one-liner suggestion that will be offered to the developer.
  - Prefer standard library (std) functions where applicable.
  - After the code fix, you MUST include a brief comment in the code explaining the fix.
    - The comment MUST ALWAYS start with the exact prefix: "Co-Hacker: "
    - Never omit or change this prefix; every fix must include it.
  - DO NOT include markdown code fences (like ```), language tags, or any explanation outside the code.
  - Keep indentation consistent with the original code.
""")

inline_assistant_prompt = ChatPromptTemplate.from_messages([INLINE_ASSISTANT_USER_PROMPT])


# Final structured chain
inline_assistant_chain: Runnable = inline_assistant_prompt | inline_assistant_llm.with_structured_output(InlineAssistantResponse)
