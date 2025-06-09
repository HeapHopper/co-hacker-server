import os

def load_openai_key() -> str:
    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY environment variable not set.")
    else:
        return os.getenv("OPENAI_API_KEY")

OPENAI_API_KEY = load_openai_key()
