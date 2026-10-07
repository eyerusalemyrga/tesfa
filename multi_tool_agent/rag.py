import json
import os
import time
from typing import Any, Dict, List
from google import genai
from google.genai import errors, types
from psycopg2.extras import RealDictCursor
from multi_tool_agent.tools.db import get_db_connection

EMBEDDING_MODEL = "text-embedding-004"


def get_gemini_client() -> genai.Client | None:
    """Initialize Google GenAI Client cleanly from environment variables."""
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[Error] GEMINI_API_KEY or GOOGLE_API_KEY environment variable is missing.")
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"[Error] Failed to initialize Google GenAI Client: {e}")
        return None


def generate_embedding(text: str) -> List[float]:
    """Generate vector embedding using the official Google GenAI SDK."""
    client = get_gemini_client()
    if not client:
        raise RuntimeError("GenAI client not initialized.")

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=768
        )
    )
    return response.embeddings[0].values


def index_document_chunk(title: str, content: str, metadata: Dict[str, Any] = None) -> bool:
    """Index a document chunk and its vector embedding into PostgreSQL pgvector."""
    try:
        vector = generate_embedding(content)
        vec_str = f"[{','.join(map(str, vector))}]"
        metadata_json = json.dumps(metadata or {})

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO tesfa.rag_embeddings 
                    (document_title, content_chunk, embedding, metadata) 
                    VALUES (%s, %s, %s::vector, %s::jsonb);
                    """,
                    (title, content, vec_str, metadata_json),
                )
                conn.commit()
        return True
    except Exception as e:
        print(f"[Error] Failed to index document chunk: {e}")
        return False


def query_rag_embeddings(query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Retrieve top_k matching document chunks by vector similarity."""
    try:
        vector = generate_embedding(query_text)
        vec_str = f"[{','.join(map(str, vector))}]"

        results = []
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT document_title, content_chunk, metadata, 
                           (embedding <=> %s::vector) AS distance 
                    FROM tesfa.rag_embeddings 
                    ORDER BY distance ASC 
                    LIMIT %s;
                    """,
                    (vec_str, top_k),
                )
                for r in cur.fetchall():
                    results.append(dict(r))
        return results
    except Exception as e:
        print(f"[Warning] RAG vector search failed: {e}")
        return []


def ask_knowledgebase(query_text: str, top_k: int = 3) -> str:
    """Retrieve context and generate response using chat interface."""
    client = get_gemini_client()
    if not client:
        return "Service unavailable: AI client could not be initialized."

    chunks = query_rag_embeddings(query_text, top_k=top_k)
    
    if not chunks:
        context_str = "No specific context found in database."
    else:
        context_str = "\n\n".join(
            [f"--- Context (Source: {c.get('document_title', 'Ref')}) ---\n{c.get('content_chunk', '')}" for c in chunks]
        )

    prompt = f"""You are Tesfa, a conflict analytics assistant.
Use the following context to answer the user's question accurately.

Context:
{context_str}

User Question: {query_text}
Answer:"""

    # Use stable, available models
    models_to_try = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash"]
    
    for model_name in models_to_try:
        for attempt in range(3):
            try:
                chat = client.chats.create(model=model_name)
                response = chat.send_message(prompt)
                if response and response.text:
                    return response.text.strip()
            except errors.APIError as e:
                if e.code == 503 and attempt < 2:
                    wait_time = (2 ** attempt) + 1
                    print(f"[Warning] 503 High Demand on {model_name}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"[Warning] Call to model {model_name} failed: {e}")
                    break
            except Exception as e:
                print(f"[Warning] Call to {model_name} failed: {e}")
                break

    return "An error occurred while processing your request due to model unavailability."
