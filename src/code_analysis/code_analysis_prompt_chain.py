from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable
from config import OPENAI_API_KEY

from code_analysis.code_analysis_models import CodeSnippet


### CODE ANALYSIS LANGCHAIN

code_analysis_llm = ChatOpenAI(
    model='gpt-4.1-nano',
    api_key=OPENAI_API_KEY
)

CODE_ANALYSIS_USER_PROMPT = HumanMessagePromptTemplate.from_template("""
Analyze code vulnerabilities in the following C / C++ code snippet:
```{snippet}```

The output should include:
- is_vulnerable: true or false
- vulnerability_type: type of issue
- vulnerability: short description
- suggest_fix: ONLY the fixed C/C++ code that addresses the vulnerability.
  - When providing the fixed code, include the entire original code with only the necessary changes applied.
  - Do not omit or collapse unchanged lines; preserve all original lines except those that require modification.
  - Prefer standard library (std) functions where applicable.
  - Include a brief comment in the code explaining the fix.
  - DO NOT include markdown code fences (like ```), language tags, or any explanation outside the code.
  - Keep indentation consistent with the original code.
""")


code_analysis_prompt = ChatPromptTemplate.from_messages([CODE_ANALYSIS_USER_PROMPT])


# Final structured chain
code_analysis_chain: Runnable = code_analysis_prompt | code_analysis_llm.with_structured_output(CodeSnippet)

