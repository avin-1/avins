from groq import AsyncGroq
from dotenv import load_dotenv
from config.api_setup import ensure_api_key

# Guarantee key exists (prompts user and saves to .env if missing)
ensure_api_key()

load_dotenv()

async_client = AsyncGroq()


__all__ = ["async_client"]
