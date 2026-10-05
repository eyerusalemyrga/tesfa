import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Use text-embedding-004 without 'models/' or text-embedding-005
EMBEDDING_MODEL = "text-embedding-004"

def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
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
    """Generates a 768-dimensional vector embedding for text."""
    if not client:
        print("[Warning] GenAI client unavailable. Returning zero vector.")
        return [0.0] * 768

    try:
        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(
                output_dimensionality=768
            )
        )
        return response.embeddings[0].values
    except Exception as e:
        print(f"[Error] Failed to generate embedding: {e}")
        return [0.0] * 768