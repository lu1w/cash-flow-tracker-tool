import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

    # defaults to "openrouter/auto" can generate token cost unexpectedly
    OPENROUTER_MODEL_ID = os.getenv("OPENROUTER_MODEL_ID")


if __name__ == "__main__":
    print(f"OPENROUTER_API_KEY = {Config.OPENROUTER_API_KEY}")
    print(f"OPENROUTER_BASE_URL = {Config.OPENROUTER_BASE_URL}")
    print(f"OPENROUTER_MODEL_ID = {Config.OPENROUTER_MODEL_ID}")
