import json
import requests

if __name__ == "__main__":
    # Support import from project root
    import sys
    from pathlib import Path
    project_root = str(Path(__file__).parent.parent.parent)
    sys.path.append(project_root)

from src.config.config import Config

OPENROUTER_BASE_URL = Config.OPENROUTER_BASE_URL
OPENROUTER_API_KEY = Config.OPENROUTER_API_KEY
OPENROUTER_MODEL_ID = Config.OPENROUTER_MODEL_ID


class OpenRouterClient:
    '''
    A client for interacting with OpenRouter model.
    Quick Start reference: https://openrouter.ai/docs/quickstart
    '''

    @staticmethod
    def chat_completion(message: str = "What is the meaning of life?"):
        response: requests.Response = requests.post(
            url=f"{OPENROUTER_BASE_URL}/chat/completions",
            headers={
                "Authorization": "Bearer " + OPENROUTER_API_KEY,
                # "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional. Site URL for rankings on openrouter.ai.
                # "X-OpenRouter-Title": "<YOUR_SITE_NAME>",  # Optional. Site title for rankings on openrouter.ai.
            },
            data=json.dumps({
                "model": OPENROUTER_MODEL_ID,
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            })
        )

        return response


if __name__ == "__main__":
    response = OpenRouterClient.chat_completion()
    print(response)
