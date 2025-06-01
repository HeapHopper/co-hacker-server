import os

def load_openai_key() -> str:
    path = "openai_token.txt"
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing {path}. Please create it with your OpenAI API key.")
    with open(path) as f:
        return f.read().strip()

OPENAI_API_KEY = load_openai_key()
