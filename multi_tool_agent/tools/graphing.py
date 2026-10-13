import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def generate_postwar_chart(metrics, title, filename):
    labels = list(metrics.keys())
    values = [float(v if v is not None else 0.0) for v in metrics.values()]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, values, color=["#e74c3c", "#3498db"])
    ax.set_title(title)

    safe_filename = filename.replace(" ", "_")
    output_dir = os.path.join(os.getcwd(), "static", "charts")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, safe_filename)
    fig.savefig(output_path)
    plt.close(fig)

    return f"/static/charts/{safe_filename}"

def generate_chart(records: list, chart_type: str = "bar") -> dict:
    """Small chart spec (labels + values) for the top conflicts."""
    return {
        "chart_type": chart_type,
        "title": "Predicted risk score of the highest-risk conflicts",
        "labels": [f"{r['country_a']} vs {r['country_b']} ({r['year']})" for r in records],
        "values": [r.get("predicted_risk_score") for r in records],
    }
