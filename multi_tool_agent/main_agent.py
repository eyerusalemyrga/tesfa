import re

from multi_tool_agent.generate import generate_conversational_response, generate_tesfa_response, wants_details, wants_evidence
from multi_tool_agent.run_log import record_run
from multi_tool_agent.tools.db import fetch_conflict_metrics
from multi_tool_agent.tools.graphing import generate_chart

def classify_query_intent(query: str) -> str:
    clean_query = query.strip().lower()

    domain_keywords = [
        "conflict", "war", "postwar", "death", "casualty", "refugee", "displacement",
        "economic", "loss", "risk", "hazard", "water", "health", "region", "country",
        "stats", "data", "metrics", "trend", "forecast", "damage", "infrastructure"
    ]

    if any(keyword in clean_query for keyword in domain_keywords):
        return "DOMAIN_ANALYTICS"

    personal_patterns = [
        r"\b(who (are|made|created) (you|tesfa))\b",
        r"\b(what( is|'s) your name)\b",
        r"\b(what (can|do) you do)\b",
        r"\b(are you (an ai|a bot|human|alive))\b",
        r"^\s*(hi|hello|hey|good (morning|afternoon|evening))\s*$",
        r"\b(how are you|how's it going|what's up)\b",
        r"\b(thank you|thanks|bye|goodbye)\b",
    ]

    for pattern in personal_patterns:
        if re.search(pattern, clean_query):
            return "PERSONAL_GENERAL"

    if len(clean_query.split()) <= 2:
        return "PERSONAL_GENERAL"

    return "DOMAIN_ANALYTICS"

GREETING_RE = re.compile(r"^\s*(hi+|hello+|hey+|hola|good (morning|afternoon|evening))\W*$", re.IGNORECASE)

def clean_text(text: str) -> str:
    return " ".join(str(text).split())

def _answer_query(user_query: str, region: str = None, conflict_type: str = None) -> dict:
    if GREETING_RE.match(user_query):
        return {
            "status": "success",
            "result": {"status": "success", "analysis_text": "Hi! How can I help you today?"},
        }

    intent = classify_query_intent(user_query)

    if intent == "PERSONAL_GENERAL":
        response_text = clean_text(generate_conversational_response(user_query))
        return {
            "status": "success",
            "result": {"status": "success", "analysis_text": response_text},
        }

    db_metrics = fetch_conflict_metrics()

    analysis_report = clean_text(generate_tesfa_response(
        user_query,
        db_metrics=db_metrics,
    ))

    if not wants_details(user_query):
        return {
            "status": "success",
            "result": {"status": "success", "analysis_text": analysis_report},
        }

    # Links, titles and the long consequence text only go out when the user asks for evidence.
    heavy_fields = set() if wants_evidence(user_query) else {"evidence_reference_links", "predicted_postwar_consequence"}
    top_conflicts = [
        {k: v for k, v in record.items() if k not in heavy_fields}
        for record in db_metrics.get("records", [])
    ]
    return {
        "status": "success",
        "result": {
            "status": "success",
            "analysis_text": analysis_report,
            "metrics": db_metrics.get("summary", {}),
            "top_conflicts": top_conflicts,
            "chart": generate_chart(top_conflicts),
        },
    }


def process_tesfa_query(user_query: str, region: str = None, conflict_type: str = None) -> dict:
    """Answer a query and record it in tesfa.runs / tesfa.steps (errors are recorded too)."""
    inputs = {"query": user_query, "region": region, "conflict_type": conflict_type}
    try:
        result = _answer_query(user_query, region, conflict_type)
    except Exception as e:
        record_run(user_query, "error", inputs, {"error": str(e)})
        raise
    record_run(user_query, "answer", inputs, {"analysis_text": result["result"]["analysis_text"]})
    return result
