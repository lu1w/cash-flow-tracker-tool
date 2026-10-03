from openai import OpenAI

if __name__ == "__main__":
    # Support import from project root
    import sys
    from pathlib import Path
    project_root = str(Path(__file__).parent.parent.parent)
    sys.path.append(project_root)

from src.utils.logger import logger

OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY = "ollama"  # An arbitrary string - connecting to locally running LLM doesn't need real authentication
LLAMA_MODEL = "llama3.2:1b"


class OllamaClient:
    def __init__(self):
        self.client = OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)

    def ping(self) -> bool:
        try:
            ping_messages = [
                {
                    "role": "user",
                    "content": "Hello"
                }
            ]
            response = self.client.chat.completions.create(
                model=LLAMA_MODEL,
                messages=ping_messages,
                max_tokens=5,
                temperature=0
            )
            content = response.choices[0].message.content
            logger.info(f"Success! Model responded: {content}")
            return True
        except Exception as e:
            logger.warning(f"Failed to ping LLM: {type(e).__name__}: {e}")
            return False


if __name__ == "__main__":
    print("Running...")
    client = OllamaClient()
    pong = client.ping()
    if pong:
        print("Successfully connected to Ollama")
    else:
        print("Failed to connect to Ollama")
