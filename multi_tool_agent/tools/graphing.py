def generate_chart(records: list, chart_type: str = "bar") -> dict:
    """Small chart spec (labels + values) for the top conflicts."""
    return {
        "chart_type": chart_type,
        "title": "Predicted risk score of the highest-risk conflicts",
        "labels": [f"{r['country_a']} vs {r['country_b']} ({r['year']})" for r in records],
        "values": [r.get("predicted_risk_score") for r in records],
    }
