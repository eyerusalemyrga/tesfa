import os
import sys
import json
from psycopg2.extras import execute_batch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from multi_tool_agent.tools.db import get_db_connection


def add_prediction_columns(cur):
    cur.execute(
        """
        ALTER TABLE tesfa.global_conflicts 
        ADD COLUMN IF NOT EXISTS predicted_postwar_consequence VARCHAR(100),
        ADD COLUMN IF NOT EXISTS predicted_risk_score FLOAT,
        ADD COLUMN IF NOT EXISTS evidence_reference_links JSONB;
    """
    )


def predict_consequences_and_links(row):
    civilian_deaths = row.get("civilian_deaths") or 0
    duration_days = row.get("duration_days") or 0
    refugees_millions = row.get("refugees_millions") or 0.0
    economic_loss = row.get("economic_loss_usd_billions") or 0.0

    risk_score = (
        (civilian_deaths / 1000.0) * 0.4
        + (duration_days / 365.0) * 0.2
        + (refugees_millions * 1.5) * 0.2
        + (economic_loss * 0.5) * 0.2
    )

    if risk_score > 10.0:
        consequence = "Severe Human & Environmental Collapse"
        links = [
            "https://academic.oup.com/exposome/article/6/1/osag003/8460765",
            "https://pmc.ncbi.nlm.nih.gov/articles/PMC12484150/",
            "https://www.unep.org/news-and-stories/statements/curbing-negative-environmental-impacts-war-and-armed-conflict",
        ]
    elif risk_score > 5.0:
        consequence = "High Displacement & Prolonged Trauma"
        links = [
            "https://www.researchgate.net/publication/259588649_Postwar_environment_and_long-term_mental_health_problems_in_former_child_soldiers_in_Northern_Uganda_The_WAYS_study",
            "https://www.un.org/en/peace-and-security/how-conflict-impacts-our-environment",
        ]
    else:
        consequence = "Moderate Reconstruction & Environmental Health Risk"
        links = [
            "https://www.researchgate.net/publication/350850248_Salting_the_Earth_Environmental_health_challenges_in_post-conflict_reconstruction",
            "https://en.wikipedia.org/wiki/Environmental_impact_of_war",
        ]

    return round(risk_score, 2), consequence, json.dumps(links)


def run_predictions():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            add_prediction_columns(cur)
            conn.commit()

            cur.execute(
                """
                SELECT id, duration_days, civilian_deaths, 
                       economic_loss_usd_billions, refugees_millions 
                FROM tesfa.global_conflicts;
            """
            )
            rows = cur.fetchall()

            updates = []
            for row in rows:
                score, consequence, links_json = predict_consequences_and_links(row)
                updates.append((consequence, score, links_json, row["id"]))

            update_query = """
                UPDATE tesfa.global_conflicts 
                SET predicted_postwar_consequence = %s,
                    predicted_risk_score = %s,
                    evidence_reference_links = %s
                WHERE id = %s;
            """
            execute_batch(cur, update_query, updates)
            conn.commit()
            print(f"Predictions and reference links attached for {len(updates)} records!")
    finally:
        conn.close()


if __name__ == "__main__":
    run_predictions()