import os
import time
from wsgiref import types
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from multi_tool_agent.rag import query_rag_embeddings

load_dotenv()

PRIMARY_MODEL = "gemini-3.8-flash"
FALLBACK_MODEL = "gemini-3.1-pro-preview"


def get_gemini_client():
    """Initialize Google GenAI Client using default settings."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[Error] GEMINI_API_KEY environment variable is missing.")
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"[Error] Failed to initialize Google GenAI Client: {e}")
        return None


def generate_tesfa_response(user_query: str, top_k: int = 3) -> str:
    """Generate response using RAG context with backoff retry and model fallback."""
    client = get_gemini_client()
    if not client:
        return "Error: Unable to initialize GenAI client."

    matches = query_rag_embeddings(user_query, top_k=top_k)

    context_str = "\n\n".join(
        [f"Source ({m.get('document_title', 'Ref')}): {m.get('content_chunk', '')}" for m in matches]
    )

    prompt = f"""You are Tesfa, an AI decision system for post-conflict impact forecasting.
Use the following retrieved context to answer the user request accurately.

Context:
{context_str if context_str else "No explicit context retrieved."}

User Query:
{user_query}
"""

    models_to_try = [PRIMARY_MODEL, FALLBACK_MODEL]
    max_retries = 3

    for model_name in models_to_try:
        for attempt in range(max_retries):
            try:
                chat = client.chats.create(model=model_name)
                response = chat.send_message(prompt)
                if response.text:
                    return response.text.strip()
            except errors.APIError as e:
                if e.code == 503 and attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + 1
                    print(f"[Warning] 503 High Demand on {model_name}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"[Warning] Call to model {model_name} failed with APIError: {e}")
                    break
            except Exception as e:
                print(f"[Warning] Unexpected error on {model_name}: {e}")
                break

    return "Error: All generation attempts failed due to service unavailability."

# In multi_tool_agent/generate.py

SYSTEM_PERSONA_PROMPT = """
You are Tesfa, an AI decision-support assistant specializing in post-conflict impact forecasting, 
environmental health risk assessment, economic loss analysis, and human displacement tracking.

When answering general or personal questions:
- Be polite, concise, and professional.
- Explain your purpose as an analytical tool for post-conflict recovery and spatial forecasting.
- Guide the user on what questions they can ask you (e.g., conflict metrics, health hazards, damage estimates).
- Do NOT generate fake conflict statistics or mention Region A/Region B unless specifically asked about sample datasets.
"""

def generate_conversational_response(user_query: str) -> str:
    """Generate direct conversational responses for personal or non-domain prompts."""
    client = get_gemini_client()
    
    response = client.models.generate_content(
       
        contents=user_query,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PERSONA_PROMPT,
            temperature=0.7
        )
    )
    return response.text