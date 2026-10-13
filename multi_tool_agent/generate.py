import json

from multi_tool_agent.llm import ask_llm
from multi_tool_agent.rag import query_rag_embeddings

def generate_tesfa_response(user_query: str, db_metrics: dict = None, top_k: int = 3) -> str:
    """Generate response using RAG context, predictions, and reference links."""
    matches = query_rag_embeddings(user_query, top_k=top_k)

    if matches:
        context_str = "\n\n".join(
            [f"Reference: {m.get('document_text', '')}" for m in matches]
        )
    else:
        context_str = "No explicit context retrieved."

    # Build metrics and predictions context
    metrics_str = ""
    if db_metrics and db_metrics.get("summary"):
        summary = db_metrics["summary"]
        metrics_str = f"Database shows {summary.get('conflict_count', 0)} conflicts with average {summary.get('avg_civilian_deaths', 0):.0f} civilian deaths, {summary.get('avg_refugees_millions', 0):.1f}M refugees, and ${summary.get('avg_economic_loss', 0):.1f}B economic loss."

    # Add top predictions with reference links
    predictions_str = ""
    if db_metrics and db_metrics.get("records"):
        predictions_str = "\nTop Risk Scenarios:\n"
        for record in db_metrics["records"][:3]:
            risk_score = record.get("predicted_risk_score", 0)
            consequence = record.get("predicted_postwar_consequence", "")
            links = record.get("evidence_reference_links", "[]")
            try:
                links_data = json.loads(links) if isinstance(links, str) else links
                links_text = "; ".join([l["title"] for l in links_data[:2]]) if links_data else ""
            except (ValueError, TypeError, KeyError):
                links_text = ""
            predictions_str += f"Risk {risk_score}/20: {consequence}. References: {links_text}\n"

    if wants_evidence(user_query):
        style_rule = "The user asked for evidence, so you may include relevant numbers and name the evidence sources."
    elif wants_details(user_query):
        style_rule = ("The user asked for specifics, so you may include relevant numbers, "
                      "but do not mention source names, studies, links, or risk scores.")
    else:
        style_rule = ("Explain in simple, friendly everyday English in one or two short paragraphs. "
                      "Do not include statistics, numbers, scores, dollar figures, links, or source names. "
                      "Describe the likely outcomes in plain words only.")
    style_rule += " Start directly with the answer; do not greet or introduce yourself."

    prompt = f"""You are Tesfa, an AI decision system for post-conflict impact forecasting.
Use the following retrieved context, metrics, and risk predictions to answer the user request accurately.

Context from Knowledge Base:
{context_str}

Conflict Metrics:
{metrics_str}

Risk Predictions with Evidence:
{predictions_str}

User Query:
{user_query}

Answer in plain text only. No markdown, no headings, no bullets, no asterisks.
{style_rule}
"""

    return ask_llm(prompt)

CONVERSATION_PROMPT = """You are Tesfa, a friendly AI assistant that helps people understand post-war conflict and its effects on people, health and the environment.
Reply to the message below like a warm, natural conversation partner.
- If it is a greeting like hi or hii, greet back briefly and ask how you can help.
- If it is about you (your name, who made you, what you can do, how you are), answer honestly: you are Tesfa, an AI assistant for post-war conflict and environmental analysis.
- If it is thanks or goodbye, respond politely.
- Keep it to one or two short sentences, plain text only, no markdown.

Message: """

EVIDENCE_WORDS = ("link", "source", "reference", "citation", "evidence", "consequence")
DETAIL_WORDS = ("number", "statistic", "stats", "figure", "data", "metric", "chart", "graph",
                "how many", "how much", "detail") + EVIDENCE_WORDS

def wants_details(query: str) -> bool:
    q = query.lower()
    return any(w in q for w in DETAIL_WORDS)

def wants_evidence(query: str) -> bool:
    q = query.lower()
    return any(w in q for w in EVIDENCE_WORDS)

def generate_conversational_response(user_query: str) -> str:
    """Generate conversational responses for personal or non-domain prompts."""
    return ask_llm(CONVERSATION_PROMPT + user_query)
