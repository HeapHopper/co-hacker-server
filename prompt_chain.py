from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable
from models import CodeSnippet
from config import OPENAI_API_KEY

from models import AskAiResponse
from langchain_core.prompts import SystemMessagePromptTemplate


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
  - Include a brief comment in the code explaining the fix.
  - DO NOT include markdown code fences (like ```), language tags, or any explanation outside the code.
  - keep identation consistent with the original code.
""")


code_analysis_prompt = ChatPromptTemplate.from_messages([CODE_ANALYSIS_USER_PROMPT])



# Final structured chain
code_analysis_chain: Runnable = code_analysis_prompt | code_analysis_llm.with_structured_output(CodeSnippet)


### ASK AI LANGCHAIN

ask_ai_llm = ChatOpenAI(
    model='gpt-4.1-mini',
    api_key=OPENAI_API_KEY
)

ASK_AI_SYSTEM_PROMPT = SystemMessagePromptTemplate.from_template("""
You are a helpful assistant for C/C++ developers.
Focus on highlighting potential bugs and security issues in the code.
If the code is correct, explain what it does in a single sentence.
If the code is incorrect, provide a short straight to the point explanation
of the issues and suggest fixes.
""")

ASK_AI_USER_PROMPT = HumanMessagePromptTemplate.from_template(""" ```{snippet}``` """)

ask_ai_prompt = ChatPromptTemplate.from_messages([
    ASK_AI_SYSTEM_PROMPT,
    ASK_AI_USER_PROMPT
])

ask_ai_chain: Runnable = ask_ai_prompt | ask_ai_llm.with_structured_output(AskAiResponse)

