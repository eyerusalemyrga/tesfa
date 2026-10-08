import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Use the current GA embedding model
EMBEDDING_MODEL = "gemini-embedding-001"

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[Error] GEMINI_API_KEY environment variable is missing in embeddings.py.")
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"[Error] Failed to initialize GenAI Client in embeddings.py: {e}")
        return None

client = get_gemini_client()

def generate_embedding(text: str) -> list[float]:
    """Generates a vector embedding for text using gemini-embedding-001."""
    if not client:
        print("[Warning] GenAI client unavailable. Returning zero vector.")
        return [0.0] * 768

    try:
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
        )
        return response.embeddings[0].values
    except Exception as e:
        print(f"[Error] Failed to generate embedding: {e}")
        return [0.0] * 768
