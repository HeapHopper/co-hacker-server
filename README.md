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


### Graph

### Prompt

### Route


## Supported features

### AskAI




