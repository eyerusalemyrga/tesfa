import json
from typing import Any, Dict, List

from google.genai import types
from psycopg2.extras import RealDictCursor

from multi_tool_agent.llm import get_client
from multi_tool_agent.tools.db import get_db_connection

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSIONS = 768  # must match the vector(768) column

def generate_embedding(text: str) -> List[float]:
    response = get_client().models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
    )
    return response.embeddings[0].values

def index_document_chunk(title: str, content: str, metadata: Dict[str, Any] = None) -> bool:
    try:
        vector = generate_embedding(content)
        vec_str = f"[{','.join(map(str, vector))}]"
        metadata_json = json.dumps(metadata or {})

        document_text = f"Title: {title}\n\nContent: {content}"

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO tesfa.rag_embeddings
                    (document_text, embedding, metadata)
                    VALUES (%s, %s::vector, %s::jsonb);
                    """,
                    (document_text, vec_str, metadata_json),
                )
                conn.commit()
        return True
    except Exception as e:
        print(f"[Error] Failed to index document chunk: {e}")
        return False

def query_rag_embeddings(query_text: str, top_k: int = 3) -> List[Dict[str, Any]]:
    try:
        vector = generate_embedding(query_text)
        vec_str = f"[{','.join(map(str, vector))}]"

        results = []
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT document_text, metadata,
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
