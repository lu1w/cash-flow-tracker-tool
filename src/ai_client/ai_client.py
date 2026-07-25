import json
import requests

if __name__ == "__main__":
    # Support import from project root
    import sys
    from pathlib import Path
    project_root = str(Path(__file__).parent.parent.parent)
    sys.path.append(project_root)

from src.config.config import OpenRouterConfig

OPENROUTER_BASE_URL = OpenRouterConfig.OPENROUTER_BASE_URL
OPENROUTER_API_KEY = OpenRouterConfig.OPENROUTER_API_KEY
OPENROUTER_MODEL_ID = "google/gemma-4-26b-a4b-it:free"


class OpenRouterClient:
    """
    A client for interacting with OpenRouter model.
    Quick Start reference: https://openrouter.ai/docs/quickstart
    """

    @staticmethod
    def chat_completion(message: str = "What is the meaning of life?"):
        response: requests.Response = requests.post(
            # endpoint doc: https://openrouter.ai/docs/api/api-reference/chat/send-chat-completion-request
            # https://openrouter.ai/docs/api/api-reference/chat/create-a-chat-completion
            url=f"{OPENROUTER_BASE_URL}/chat/completions",
            headers={
                "Authorization": "Bearer " + OPENROUTER_API_KEY,
                # "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional. Site URL for rankings on openrouter.ai.
                # "X-OpenRouter-Title": "<YOUR_SITE_NAME>",  # Optional. Site title for rankings on openrouter.ai.
            },
            data=json.dumps({
                "messages": [
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                # Optional params:
                "model": OPENROUTER_MODEL_ID,
                "reasoning": {"effort": "medium", "summary": "concise"},
                "metadata": {},
                "user": "cash-flow-tracker-tool",  # User ID
            })
        )

        return response


if __name__ == "__main__":
    response = OpenRouterClient.chat_completion()
    print(response)
    print("-----")
    print(response.json())
