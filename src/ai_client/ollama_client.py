from openai import OpenAI

if __name__ == "__main__":
    # Support import from project root
    import sys
    from pathlib import Path
    project_root = str(Path(__file__).parent.parent.parent)
    sys.path.append(project_root)

from src.utils.logger import logger
from src.config.config import AIConfig

OLLAMA_BASE_URL = AIConfig.OLLAMA_BASE_URL
OLLAMA_API_KEY = AIConfig.OLLAMA_API_KEY
OLLAMA_MODEL = AIConfig.OLLAMA_MODEL


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
                model=OLLAMA_MODEL,
                messages=ping_messages,
                max_tokens=5,
                temperature=0
            )
            content = response.choices[0].message.content
            logger.info(f"Pong! Model responded: {content}")
            return True
        except Exception as e:
            logger.exception(f"Failed to ping Ollama {OLLAMA_MODEL}: {e}")
            return False


if __name__ == "__main__":
    print("Running...")
    client = OllamaClient()
    pong = client.ping()
    if pong:
        print("Successfully connected to Ollama")
    else:
        print("Failed to connect to Ollama")
