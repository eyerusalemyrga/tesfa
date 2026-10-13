import os
import time
from functools import lru_cache

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()

# Tried in order; if one is overloaded or out of quota we move on to the next.
MODELS_TO_TRY = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-flash-latest", "gemini-3.1-flash-lite"]
REQUEST_TIMEOUT_MS = 20_000
MAX_ATTEMPTS = 3
QUOTA_COOLDOWN_SECONDS = 60
TOTAL_BUDGET_SECONDS = 45  # stop trying more models/retries after this long

_skip_until: dict[str, float] = {}  # model -> time before which we don't try it again


class LLMUnavailableError(RuntimeError):
    """Every model failed (overloaded, out of quota, or timed out)."""


@lru_cache(maxsize=1)
def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise LLMUnavailableError("GEMINI_API_KEY is not set.")
    return genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_MS))


def ask_llm(prompt: str) -> str:
    """Send a prompt to Gemini and return the text, falling back across models."""
    client = get_client()
    deadline = time.time() + TOTAL_BUDGET_SECONDS
    for model in MODELS_TO_TRY:
        if time.time() > deadline:
            break
        if _skip_until.get(model, 0) > time.time():
            continue
        for attempt in range(MAX_ATTEMPTS):
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                if response and response.text:
                    return response.text.strip()
                break
            except errors.APIError as e:
                if e.code == 503 and attempt < MAX_ATTEMPTS - 1 and time.time() < deadline:
                    wait = 2 ** attempt + 1
                    print(f"[Warning] {model} overloaded (503). Retrying in {wait}s...")
                    time.sleep(wait)
                    continue
                if e.code == 429:
                    print(f"[Warning] {model} is out of quota; skipping it for {QUOTA_COOLDOWN_SECONDS}s.")
                    _skip_until[model] = time.time() + QUOTA_COOLDOWN_SECONDS
                else:
                    print(f"[Warning] {model} failed: {e}")
                break
            except Exception as e:
                print(f"[Warning] {model} failed: {e}")
                break
    raise LLMUnavailableError("All Gemini models failed.")
