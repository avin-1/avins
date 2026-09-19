"""
API Key Setup — Hardcoded safety net for GROQ_API_KEY.

This module is imported at the very top of every client module
(config/asyncModel.py, config/model.py).  It guarantees that by the
time a Groq client is instantiated, GROQ_API_KEY is present both in
os.environ and persisted in the project's .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv, set_key

# Always resolve .env relative to this file's project root
ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


def ensure_api_key() -> str:
    """
    Ensure GROQ_API_KEY exists and is non-empty.

    Priority order:
      1. Already set in os.environ (e.g. system environment)
      2. Found in .env file
      3. Prompted from the user → saved to .env for future runs

    Returns the validated API key string.
    """
    # Load .env into os.environ (safe even if file doesn't exist)
    load_dotenv(ENV_FILE, override=False)

    key = os.environ.get("GROQ_API_KEY", "").strip()

    if key:
        return key  # Already available — nothing to do

    # ── Key is missing: inform and prompt ─────────────────────────────
    print()
    print("=" * 58)
    print("  ⚠  GROQ API Key not found.")
    print("  Get yours free at: https://console.groq.com/keys")
    print("=" * 58)

    while not key:
        key = input("  Enter your GROQ_API_KEY: ").strip()
        if not key:
            print("  Key cannot be empty. Please try again.")

    # ── Persist to .env ────────────────────────────────────────────────
    ENV_FILE.touch(exist_ok=True)          # create .env if it doesn't exist
    set_key(str(ENV_FILE), "GROQ_API_KEY", key)
    os.environ["GROQ_API_KEY"] = key       # make available in current process

    print()
    print("  ✔  API key saved to .env — you won't be asked again.")
    print("=" * 58)
    print()

    return key


__all__ = ["ensure_api_key"]
