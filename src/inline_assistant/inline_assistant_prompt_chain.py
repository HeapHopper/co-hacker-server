from typing import Annotated
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessage
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



### Complex Graph stuff

### initial_classifier
initial_classifier_prompt = ChatPromptTemplate.from_messages([
    SystemMessage("You are a static code classifier that categorizes a C/C++ line of code based on security characteristics."),
    HumanMessagePromptTemplate.from_template("""
Line:
```c++
{line}
```
 {scope}
{file}
Return a JSON object like:
{
"confidence_level": float, // 0.0 to 1.0
"unsafe_pattern_detected": bool,
"suggestion_type": "safe" | "vulnerable" | "std_upgrade" | "scope_check" | "file_check"
}
""")
])

initial_classifier_chain: Runnable = initial_classifier_prompt | inline_assistant_llm.with_structured_output(
    schema=Annotated[dict, {
        "confidence_level": float,
        "unsafe_pattern_detected": bool,
        "suggestion_type": str
    }]
)

### handle_safe

# No prompt is needed for handling a safe code, nothing to generate :-) !

### handle_vulnerable

vulnerability_prompt = ChatPromptTemplate.from_messages([
    SystemMessage("You are a C++ secure coding expert. Find and fix vulnerabilities."),
    HumanMessagePromptTemplate.from_template("""
Analyze this code:
```c++
{line}
```
{scope}
{file}
Respond with JSON:
{
"is_vulnerable": true,
"vulnerability": {
"description": "...",
"vulnerable_code": "..."
},
"suggest_fix": "..."
}
""")
])

vulnerability_chain: Runnable = vulnerability_prompt | inline_assistant_llm.with_structured_output(InlineAssistantResponse)



### check_scope

scope_check_prompt = ChatPromptTemplate.from_messages([
    SystemMessage("You analyze scope-level security in C++."),
    HumanMessagePromptTemplate.from_template("""
Line:
```c++
{line}
                                             {scope}
                                             Are there any risks like Use After Free, Out-of-Bounds access, Double Free, etc.?

Respond JSON:
{
"confidence_level": float,
"suggestion_type": "vulnerable" | "std_upgrade" | "file_check" | "safe"
}
""")
])

scope_check_chain = scope_check_prompt | inline_assistant_llm.with_structured_output(
schema=Annotated[dict, {
"confidence_level": float,
"suggestion_type": str
}]
)


### check_file

# check file will use the same chain as check_scope, but giving the entire file as scope!



### suggest_std_upgrade

std_upgrade_prompt = ChatPromptTemplate.from_messages([
    SystemMessage("You convert legacy or unsafe C++ code to use modern C++ features."),
    HumanMessagePromptTemplate.from_template("""
Line:
```c++
{line}
                                             If applicable, suggest replacing it with std::vector, std::copy, smart pointers, or similar safer features.

Respond JSON:
{
"is_vulnerable": false,
"vulnerability": {
"description": "Safe but can be improved with std library.",
"vulnerable_code": "...original line..."
},
"suggest_fix": "...modern equivalent..."
}
""")
])

std_upgrade_chain = std_upgrade_prompt | inline_assistant_llm.with_structured_output(InlineAssistantResponse)