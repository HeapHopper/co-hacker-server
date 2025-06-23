# co-hacker-server
co-hacker-server

## The Co-Hacker VSCode extension

This repository is a FastAPI backend service for the [Co-Hacker](https://github.com/HeapHopper/co-hacker) VSCode extension. But it is also where the AI models, prompts and structured queries are defined and implemented, rather than just a REST queries router.

Co-Hacker is a co-pilot extension made by developers for developers, intending to find software insecurities in development time - before compilation and/or runtime phases - providing "on-the-fly" solutions to vulnerable code.

In practice, the VSCode extension is just a simple client-side logic extracting code selections to be examined and replacing vulnerable code with a secure one. It does not have any direct contact with the LLM itself and is unaware of any AI agent behavior.

The queries from the VSCode extension are routed to their designated endpoint in this server, where each request for automatic or manual code analysis is processed using the right LLM model (not to confuse with model in the context of `BaseModel`) with a prompt specifying the secure-code mission.

This service is hosted online on [railway.app](https://railway.com/).

## Working principle

Co-Hacker supports several features - some a are automatic and some manual - but the working principle for how a code snippet is being assessed to be secure or not, how a fix suggestion is being generated and how it can be applied back to the user code - is the same for all cases.

To make things more things more tangible we will follow the `inline_assistant` feature which is an automatic mechanism to find code vulnerabilities in a certain line of code. But the process milestones are the same for all other features.

### Model

Each use case starts with a strict model for the feature request and response properties:

```python
class InlineAssistantRequest(BaseModel):
    current_line: str
    current_scope: str
    current_file: str

class InlineAssistantResponse(BaseModel):
    is_vulnerable: bool
    vulnerability: Vulnerability
    suggest_fix: str
```

In the case of `inline_assistant`, the server expects to receive the current line of code, along with the current scope (`{}`) and the current file. This data should be sufficient for determine whether the line has a potential security risk.

In return, the service is committing to provide the following information: is the code secure, if not what is the vulnerability, and how can it be fixed. Later those properties are used by the client (the VSCode extension) to modify the code or present warnings / solutions in the editor.

### Prompt

After defining the request and response scheme, it is time to create a prompt which will generate the desired response, based on given request. The "Prompt" step is composed of three steps:

#### 1. LLM definition

for example:

```python
inline_assistant_llm = ChatOpenAI(
    model='gpt-4.1-nano',
    api_key=OPENAI_API_KEY
)
```

the `inline_assistant` uses the `nano` model for fast, "real time" response latency.

#### 2. Prompt Templates

Using [langchain](https://www.langchain.com/) module objects like `HumanMessagePromptTemplate`, `SystemMessagePromptTemplate` etc. we create a prompt (single or chain) for the task of inline code assistant.

The prompt refers to data given in the request model, for example:

```python
INLINE_ASSISTANT_USER_PROMPT = HumanMessagePromptTemplate.from_template("""
You are a C/C++ inline code assistant ... focusing on vulnerability detection and secure code.
                                                                        
start with analyzing the current line of code:
```{line}```
                                                                        
The current scope is also provided for context...
```{scope}```
```

The prompt mentions the response model as well:

```python
"""
The output should include:
- is_vulnerable: true or false
- vulnerability:
    - description: a brief description of the vulnerability
    - vulnerable_code: the specific code that is vulnerable
- suggest_fix: ONLY the fixed C/C++ code that addresses the vulnerability.
"""
```

This step is finished with a `ChatPromptTemplate` instance, provided by `langchain` for making an LLM specific prompt instance.

#### Creating Runnable

using `langchain.Runnable` the previous prompt templates are now an action that can be run to generate structured response:

```python
inline_assistant_chain: Runnable = inline_assistant_prompt | inline_assistant_llm.with_structured_output(InlineAssistantResponse)
```

### Graph

We finished the last step with a `langchain.Runnable` instance. Using `invoke()` we can send a structured query to the LLM and use the results. But we lack one thing which is very important in production: Tracing.

The "Graph" step has two tasks:

#### Traceable nodes

Each runnable should have its own "node" - a function that wraps the `invoke()` method with given request and response data. This node is being traced using `traceable` decorator by `langsmith` module:

```python
# LangGraph-compatible state
class InlineAssistantGraphState(BaseModel):
    input: InlineAssistantRequest
    output: InlineAssistantResponse | None = None  

# Single-node LangGraph
@traceable(name="inline_assistant", description="Inline code assistant for C/C++ vulnerabilities")
def inline_assistant_node(state: InlineAssistantGraphState) -> dict:
    result = inline_assistant_chain.invoke({
        "line": state.input.current_line,
        "scope": state.input.current_scope,
        "file": state.input.current_file
    })
    return {"output": result}
```

#### Build complex graph

Using `langgraph` we can orchestrate those nodes into a complex graph, contacting `Runnable` actions to create even more concrete solution to each case.

For now, the graph is composed of single graph:

```python
def build_inline_assistant_graph():
    builder = StateGraph(InlineAssistantGraphState)
    builder.add_node("inline_assistant", inline_assistant_node)
    builder.set_entry_point("inline_assistant")
    builder.set_finish_point("inline_assistant")
    return builder.compile()
```

### Route


## Supported features

### AskAI




