import os
import uuid
import json
import time
import re
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
from google import genai
from google.genai import errors
from multi_tool_agent.embeddings import generate_embedding

from multi_tool_agent.tools.db import get_db_connection
from multi_tool_agent.rag import generate_embedding
from typing import Any, Dict, List
from multi_tool_agent.generate import generate_conversational_response, generate_tesfa_response
from multi_tool_agent.rag import ask_knowledgebase
from multi_tool_agent.tools.db import fetch_conflict_metrics
from multi_tool_agent.tools.graphing import generate_chart


load_dotenv()

STATIC_DIR = Path("static")
CHARTS_DIR = STATIC_DIR / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

PRIMARY_MODEL = "gemini-3.8-flash"
FALLBACK_MODEL = "gemini-3.1-pro-preview"

PLAIN_ENGLISH_PROMPT = """
You are an expert environmental health specialist for the Tesfa Post-War Conflict & Environmental Analysis system.

Using the provided conflict metrics and literature context, explain the post-war environmental health risks in clear, natural, standard English.

Formatting Constraints:
- Write in continuous, well-structured paragraphs.
- DO NOT use Markdown headers (no #, ##, or ###).
- DO NOT use bullet points or numbered lists.
- DO NOT use academic citation tags or numbers (no [1], [2], or inline reference numbers).
- Explain technical terms naturally in plain language so any non-technical reader can easily understand.
"""


def get_gemini_client():
    """Initialize Google GenAI Client using default settings."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[Error] GEMINI_API_KEY environment variable is missing.")
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception as e:
        print(f"[Error] Failed to initialize Google GenAI Client: {e}")
        return None


def generate_llm_response(client, prompt: str) -> str:
    """Invokes Google GenAI models using Chat sessions to support AFC cleanly with retry logic."""
    models_to_try = [PRIMARY_MODEL, FALLBACK_MODEL]
    
    for model_name in models_to_try:
        for attempt in range(4):
            try:
                # Use client.chats instead of client.models to eliminate the AFC warning
                chat = client.chats.create(model=model_name)
                response = chat.send_message(prompt)
                if response.text:
                    return response.text.strip()
            except errors.APIError as e:
                if e.code == 503 and attempt < 3:
                    wait_time = (2 ** attempt) + 1
                    print(f"[Warning] 503 High Demand on {model_name}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"[Warning] Model {model_name} failed with API error: {e}")
                    break
            except Exception as e:
                print(f"[Warning] Call to {model_name} failed: {e}")
                break
                
    raise RuntimeError("All LLM generation attempts failed.")

def search_rag_embeddings(query: str, conn, top_k: int = 3) -> list:
    """Retrieve relevant literature chunks using vector search."""
    try:
        query_vector = generate_embedding(query)
        vec_str = f"[{','.join(map(str, query_vector))}]"

        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            sql = """
                SELECT document_title AS title, content_chunk AS content, metadata, 
                       (embedding <=> %s::vector) as distance
                FROM tesfa.rag_embeddings
                ORDER BY distance ASC
                LIMIT %s;
            """
            cur.execute(sql, (vec_str, top_k))
            return cur.fetchall()
    except Exception as e:
        print(f"[Warning] RAG vector search failed: {e}")
        return []


def process_tesfa_query(
    query: str,
    target_region: str | None = None,
    conflict_type: str | None = None,
) -> dict:
    """Consolidated single-agent processor generating plain English analytical text."""
    run_id = str(uuid.uuid4())
    conn = get_db_connection()
    client = get_gemini_client()

    try:
        # 1. Fetch aggregate stats and sample records from PostgreSQL
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            where_clauses = []
            params = []

            if target_region:
                where_clauses.append("LOWER(region) = LOWER(%s)")
                params.append(target_region)
            if conflict_type:
                where_clauses.append("LOWER(conflict_type) = LOWER(%s)")
                params.append(conflict_type)

            where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            sql_query = f"""
                SELECT 
                    COUNT(*) as conflict_count,
                    AVG(civilian_deaths) as avg_civilian_deaths,
                    AVG(military_deaths_a + military_deaths_b) as avg_military_deaths,
                    AVG(duration_days) as avg_duration_days,
                    AVG(economic_loss_usd_billions) as avg_economic_loss,
                    AVG(refugees_millions) as avg_refugees_millions,
                    SUM(refugees_millions) as total_refugees_millions
                FROM tesfa.global_conflicts
                {where_sql};
            """
            cur.execute(sql_query, params)
            stats = cur.fetchone() or {}

            metrics = {
                "conflict_count": stats.get("conflict_count") or 0,
                "avg_civilian_deaths": float(stats.get("avg_civilian_deaths") or 0),
                "avg_military_deaths": float(stats.get("avg_military_deaths") or 0),
                "avg_economic_loss": float(stats.get("avg_economic_loss") or 0),
                "avg_refugees_millions": float(stats.get("avg_refugees_millions") or 0),
                "total_refugees_millions": float(stats.get("total_refugees_millions") or 0),
            }

            top_records_query = """
                SELECT country_a, country_b, conflict_type, year, 
                       civilian_deaths, economic_loss_usd_billions, outcome
                FROM tesfa.global_conflicts
                ORDER BY civilian_deaths DESC NULLS LAST
                LIMIT 5;
            """
            cur.execute(top_records_query)
            top_conflicts = cur.fetchall()

        # 2. Vector context search
        rag_docs = search_rag_embeddings(query, conn, top_k=3)

    except Exception as e:
        print(f"[Error] Database query processing failed: {e}")
        if conn:
            conn.close()
        return {"status": "error", "error": str(e)}
    finally:
        if conn:
            conn.close()

    # 3. LLM Synthesis using plain English constraints
    if client:
        rag_context_str = ""
        for i, doc in enumerate(rag_docs, start=1):
            title = doc.get("title", "Literature Reference")
            rag_context_str += f"\n- Document Title: {title}\nExcerpt: {doc.get('content', '')}\n"

        prompt = f"""
{PLAIN_ENGLISH_PROMPT}

User Question: "{query}"

System Metrics:
{json.dumps(metrics, indent=2)}

Conflict Case Samples:
{json.dumps(top_conflicts, default=str, indent=2)}

Retrieved Literature Context:
{rag_context_str if rag_context_str else "Standard environmental health and post-war reconstruction literature."}
"""
        try:
            analysis_text = generate_llm_response(client, prompt)
        except Exception as e:
            print(f"[Error] LLM text generation failed completely: {e}")
            analysis_text = _fallback_summary(metrics)
    else:
        analysis_text = _fallback_summary(metrics)

    # 4. Generate Visualization Chart
    chart_filename = f"postwar_{uuid.uuid4().hex[:8]}.png"
    chart_path = CHARTS_DIR / chart_filename

    fig, ax = plt.subplots(figsize=(6, 4))
    categories = ["Civilian Deaths", "Military Deaths"]
    values = [metrics["avg_civilian_deaths"], metrics["avg_military_deaths"]]

    ax.bar(categories, values, color=["#d9534f", "#0275d8"])
    ax.set_title("Average Conflict Fatalities")
    ax.set_ylabel("Count")
    plt.tight_layout()
    plt.savefig(chart_path)
    plt.close(fig)

    return {
        "run_id": run_id,
        "status": "success",
        "result": {
            "status": "success",
            "analysis_text": analysis_text,
            "metrics": metrics,
            "top_conflicts": top_conflicts,
            "chart_url": f"/static/charts/{chart_filename}",
        },
    }


def _fallback_summary(metrics: dict) -> str:
    return (
        f"Analysis across {metrics['conflict_count']} records indicates "
        f"average civilian deaths of {metrics['avg_civilian_deaths']:,.0f}, "
        f"military deaths of {metrics['avg_military_deaths']:,.0f}, and an "
        f"average economic loss of ${metrics['avg_economic_loss']:.2f}B USD."
    )



# Keyword and pattern matches for general / personal queries
PERSONAL_AND_GENERAL_PATTERNS = [
    # Identity & Persona
    r"\b(who (are|made|created) (you|tesfa))\b",
    r"\b(what( is|'s) your name)\b",
    r"\b(what (can|do) you do)\b",
    r"\b(are you (an ai|a bot|human|alive))\b",
    
    # Greetings & Small Talk
    r"^\s*(hi|hii|hiii|hello|hey|heyy|greetings|good (morning|afternoon|evening))\s*$",
    r"\b(how are you|how's it going|what's up)\b",
    r"\b(thank you|thanks|bye|goodbye)\b",
    
    # Off-topic / Personal Advice
    r"\b(tell me a joke|what is the meaning of life|do you like|what is your favorite)\b",
]

# Keywords that explicitly indicate a domain query (overrides small talk)
DOMAIN_KEYWORDS = [
    "conflict", "war", "postwar", "death", "casualty", "refugee", "displacement",
    "economic", "loss", "risk", "hazard", "water", "health", "region", "country",
    "stats", "data", "metrics", "trend", "forecast", "damage", "infrastructure"
]

def classify_query_intent(query: str) -> str:
    """
    Classifies intent as 'PERSONAL_GENERAL' or 'DOMAIN_ANALYTICS'.
    """
    clean_query = query.strip().lower()
    
    # 1. Check if the user query contains domain-specific terminology
    if any(keyword in clean_query for keyword in DOMAIN_KEYWORDS):
        return "DOMAIN_ANALYTICS"
        
    # 2. Check against personal/conversational regex patterns
    for pattern in PERSONAL_AND_GENERAL_PATTERNS:
        if re.search(pattern, clean_query):
            return "PERSONAL_GENERAL"
            
    # 3. Very short non-domain queries (e.g., <= 2 words without domain terms)
    if len(clean_query.split()) <= 2:
        return "PERSONAL_GENERAL"

    return "DOMAIN_ANALYTICS"

def process_tesfa_query(user_query: str, region: str = None, conflict_type: str = None) -> Dict[str, Any]:
    # Determine the query intent
    intent = classify_query_intent(user_query)

    # ------------------------------------------------------------------
    # PATH A: Personal / Conversational / Off-topic Queries
    # ------------------------------------------------------------------
    if intent == "PERSONAL_GENERAL":
        # Generate a conversational answer using standard Gemini model (no RAG)
        response_text = generate_conversational_response(user_query)
        
        return {
            "status": "success",
            "result": {
                "status": "success",
                "analysis_text": response_text,
                "metrics": {
                    "conflict_count": 0,
                    "avg_civilian_deaths": 0.0,
                    "avg_military_deaths": 0.0,
                    "avg_economic_loss": 0.0,
                    "avg_refugees_millions": 0.0,
                    "total_refugees_millions": 0.0
                },
                "top_conflicts": [],
                "chart_url": None
            }
        }

    # ------------------------------------------------------------------
    # PATH B: Domain Analytical Queries (Run RAG + SQL DB)
    # ------------------------------------------------------------------
    # 1. RAG Vector Search
    rag_context = ask_knowledgebase(user_query)
    
    # 2. SQL Database Aggregation
    db_metrics = fetch_conflict_metrics(user_query, region, conflict_type)
    
    # 3. Report Generation
    analysis_report = generate_tesfa_response(user_query, rag_context, db_metrics)
    
    return {
        "status": "success",
        "result": {
            "status": "success",
            "analysis_text": analysis_report,
            "metrics": db_metrics["summary"],
            "top_conflicts": db_metrics["records"],
            "chart_url": generate_chart(db_metrics)
        }
    }