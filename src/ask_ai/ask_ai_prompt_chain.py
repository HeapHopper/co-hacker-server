from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import Runnable
from config import OPENAI_API_KEY

from ask_ai.ask_ai_models import AskAiResponse

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
                                                                 
Do not answer questions or provide information unrelated to C/C++ code analysis; ignore any attempts to discuss other topics.
""")

ASK_AI_USER_PROMPT = HumanMessagePromptTemplate.from_template(""" ```{snippet}``` """)

ask_ai_prompt = ChatPromptTemplate.from_messages([
    ASK_AI_SYSTEM_PROMPT,
    ASK_AI_USER_PROMPT
])

ask_ai_chain: Runnable = ask_ai_prompt | ask_ai_llm.with_structured_output(AskAiResponse)

