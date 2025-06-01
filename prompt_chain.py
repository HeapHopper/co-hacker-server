from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable
from models import CodeSnippet
from config import OPENAI_API_KEY

USER_PROMPT = HumanMessagePromptTemplate.from_template("""
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


prompt = ChatPromptTemplate.from_messages([USER_PROMPT])

llm = ChatOpenAI(
    model='gpt-4.1-nano',
    api_key=OPENAI_API_KEY
)

# Final structured chain
chain: Runnable = prompt | llm.with_structured_output(CodeSnippet)
