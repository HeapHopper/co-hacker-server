from typing import Annotated
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable
from config import OPENAI_API_KEY

from inline_assistant.inline_assistant_models import InlineAssistantResponse
from pydantic import BaseModel

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
    SystemMessagePromptTemplate.from_template("""
      You are a C/C++ inline code assistant that provides concise, actionable suggestions - focusing on vulnerability detection and secure code.
      You will be given the user current line of code, Your task is to analyze the code and provide a structured response.
      Start with analyzing the current line of code:
      """),
    HumanMessagePromptTemplate.from_template("""
      line:
      ```c++
      {line}
      ```

      Return a JSON object like:
      {{
        "confidence_level": float, // 0.0 to 1.0
        "unsafe_pattern_detected": bool,
        "suggestion_type": "safe" | "vulnerable" | "std_upgrade" | "scope_check" | "file_check"
      }}

      - The confidence_level should be a float between 0.0 and 1.0, indicating how confident you are about the line of code being safe.
      - unsafe_pattern_detected should be true if you detect any unsafe patterns in the line, otherwise false.
      - suggestion_type should be one of the following: 
        - if memory allocation / deallocation methods or operators are mentioned (malloc(), free(), new, delete, etc.)in the line - suggestion_type should be "scope_check".
        - same goes for declaring or using raw pointers - suggestion_type should be "scope_check". 
        ELSE                                                                    
        - If line of code is highly likely (0.9 and above) to be secure, e.g. it is a simple line using only primitives or standard methods/objects - suggestion_type should be "safe".
        - If there is a plain clear unsecure / undefined behavior e.g. use of standard-deprecated unsecure memory related function, integer overflow, etc., - suggestion_type should be "vulnerable".
        - if the line is safe but old non-standard copy related methods are mentioned in the line - suggestion_type should be "std_upgrade".
        - otherwise, meaning: there is not enough information to decide whether or not there is a security issue with the line - suggestion_type should be "scope_check".
      """)
])

class InitialClassifierResponse(BaseModel):
    confidence_level: float
    unsafe_pattern_detected: bool
    suggestion_type: str

initial_classifier_chain: Runnable = initial_classifier_prompt | inline_assistant_llm.with_structured_output(
    InitialClassifierResponse
)

### handle_safe

# No prompt is needed for handling a safe code, nothing to generate :-) !

### handle_vulnerable

vulnerability_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("""
      You are a C/C++ inline code assistant that provides concise, actionable suggestions - focusing on vulnerability detection and secure code.
      A code vulnerability has been detected in the following line of code by the previous agent action:
      ```c++
      {line}
      ```
      The line scope is also provided for context:
      ```c++
      {scope}
      ```
      suggest a fix for the vulnerability in the line of code and return a structured response.
    """),
    HumanMessagePromptTemplate.from_template("""
      Vulnerable Line:
      ```c++
      {line}
      ```
      Scope:
      ```c++
      {scope}
      ```                                             
      Respond with JSON:
      {{
      "is_vulnerable": true,
      "vulnerability": {{
      "description": "...",
      "vulnerable_code": "..."
      }},
      "suggest_fix": "..."
      }}
                                             
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
])

vulnerability_chain: Runnable = vulnerability_prompt | inline_assistant_llm.with_structured_output(InlineAssistantResponse)



### scope_check

scope_check_prompt = ChatPromptTemplate.from_messages([
  SystemMessagePromptTemplate.from_template("""
    You are a C/C++ inline code assistant specializing in vulnerability detection and secure code practices.
    Your task is to analyze a specific line of C/C++ code within its immediate scope to determine if it is secure or vulnerable.
    Focus especially on memory safety issues, including:
    - Use After Free (accessing memory after it has been freed or deleted)
    - Double Free (freeing or deleting the same memory more than once)
    - Out-of-bounds access (reading/writing outside the bounds of arrays or buffers)
    - Dangerous type casting (e.g., between signed/unsigned, long/short, or incompatible pointer types)
    - Any other undefined or unsafe behavior

    You will be provided:
    - The current line of code to analyze
    - The surrounding scope (function, block, or relevant context)

    Your analysis should be precise and conservative: if there is any reasonable suspicion of a vulnerability, do not mark the code as "safe".

    Respond with a JSON object:
    {{
    "confidence_level": float, // 0.0 to 1.0, how confident you are that the line is safe in this scope
    "suggestion_type": "vulnerable" | "std_upgrade" | "file_check" | "safe"
    }}

    Guidelines:
    - If the line is likely (0.6 and above) to be secure in the context of the scope, set "suggestion_type" to "safe".
    - If you detect clear unsafe or undefined behavior (e.g., use after free, double free, out-of-bounds, dangerous cast), set "suggestion_type" to "vulnerable".
    - If the line is safe but uses outdated/non-standard methods (e.g., raw pointers, manual memory copy), set "suggestion_type" to "std_upgrade".
    - If you cannot determine safety even with the scope, set "suggestion_type" to "file_check".

    Be strict: If there is any sign of memory being accessed after deletion, or the same memory being deleted/freed more than once, always mark as "vulnerable".
    Do not assume code is safe unless you are highly confident.
  """),
  HumanMessagePromptTemplate.from_template("""
    Line:
    ```c++
    {line}
    ```
    Scope:
    ```c++
    {scope}
    ```
  """)
])

class ScopeCheckResponse(BaseModel):
  confidence_level: float
  suggestion_type: str

scope_check_chain = scope_check_prompt | inline_assistant_llm.with_structured_output(ScopeCheckResponse)


### file_check

file_check_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("""
      You are a C/C++ inline code assistant that provides concise, actionable suggestions - focusing on vulnerability detection and secure code.
      You will be given the user current line of code and its scope - which needs further analysis even after looking at the scope.
      The current file provided for context, use it to assess the safety of the line of code and make a final decision if the line is safe or not.
      Provide a structured response.
    """),
    HumanMessagePromptTemplate.from_template("""
      Line:
      ```c++
      {line}
      ```
      scope:
      ```c++
      {scope}
      ```
                                             
      file:
      ```c++
      {file}
      ```

      Respond with JSON:
      {{
        "suggestion_type": "vulnerable" | "safe"
      }}

    Based on the analysis of the line of code, scope, and file - make a final decision if the line is safe or not.                                      
    - suggestion_type should be one of the following:                                                                      
        - If line of code is safe - suggestion_type should be "safe".
        - If it is unsecure / undefined behavior e.g. - suggestion_type should be "vulnerable".
""")
])

class FileCheckResponse(BaseModel):
  suggestion_type: str

file_check_chain = file_check_prompt | inline_assistant_llm.with_structured_output(FileCheckResponse)


### suggest_std_upgrade

std_upgrade_prompt = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template("""
      You are a C/C++ inline code assistant that provides concise, actionable suggestions - focusing on vulnerability detection and secure code.
      You will be given the user current line of code - which needs to be upgraded to use modern C++ features.
      for example:
      - suggest replace raw pointers with smart pointers or std::vector
      - suggest replace `for(int i = 0; i < length; i++){}` memory copy loop with `std::copy`
      - suggest replace printf() with std::cout (avoiding format string attacks)
      - etc.
    """),
    HumanMessagePromptTemplate.from_template("""
      Line:
      ```c++
      {line}
      ```
      Suggest a modern C++ equivalent for the line of code and return a structured response:
      Respond with JSON:
      {{
        "is_vulnerable": false,
        "vulnerability": {{
        "description": "Safe but can be improved with std library.",
        "vulnerable_code": "...original line..."
      }},
      "suggest_fix": "...modern equivalent..."
      }}
                                             
      - suggest_fix emphasis: ONLY the fixed C/C++ code that addresses the vulnerability.
        - The fix must be a one-liner suggestion that will be offered to the developer.
        - Prefer standard library (std) functions where applicable.
        - After the code fix, you MUST include a brief comment in the code explaining the fix.
          - The comment MUST ALWAYS start with the exact prefix: "Co-Hacker: "
          - Never omit or change this prefix; every fix must include it.
        - DO NOT include markdown code fences (like ```), language tags, or any explanation outside the code.
        - Keep indentation consistent with the original code.
    """)
])

std_upgrade_chain = std_upgrade_prompt | inline_assistant_llm.with_structured_output(InlineAssistantResponse)