import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    """Connect with DATABASE_URL if set (hosted databases such as Supabase), else the POSTGRES_* settings."""
    database_url = (os.getenv("DATABASE_URL") or "").strip()  # pasted values often carry a trailing newline
    if database_url:
        return psycopg2.connect(database_url, cursor_factory=RealDictCursor)
    return psycopg2.connect(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        cursor_factory=RealDictCursor,
    )

def fetch_conflict_metrics() -> dict:
    """Fetch summary metrics and top conflicts with predictions."""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        COUNT(*) AS conflict_count,
                        AVG(civilian_deaths) AS avg_civilian_deaths,
                        AVG(military_deaths_a + military_deaths_b) AS avg_military_deaths,
                        AVG(economic_loss_usd_billions) AS avg_economic_loss,
                        AVG(refugees_millions) AS avg_refugees_millions,
                        SUM(refugees_millions) AS total_refugees_millions
                    FROM tesfa.conflicts;
                """)
                row = cur.fetchone() or {}

                # Top conflicts with predictions and references
                cur.execute("""
                    SELECT
                        id,
                        country_a,
                        country_b,
                        conflict_type,
                        year,
                        civilian_deaths,
                        economic_loss_usd_billions,
                        refugees_millions,
                        outcome,
                        predicted_risk_score,
                        risk_category,
                        predicted_postwar_consequence,
                        evidence_reference_links
                    FROM tesfa.conflicts_full
                    WHERE predicted_risk_score IS NOT NULL
                    ORDER BY predicted_risk_score DESC NULLS LAST
                    LIMIT 5;
                """)
                records = cur.fetchall()

                summary = {
                    "conflict_count": int(row.get("conflict_count") or 0),
                    "avg_civilian_deaths": float(row.get("avg_civilian_deaths") or 0),
                    "avg_military_deaths": float(row.get("avg_military_deaths") or 0),
                    "avg_economic_loss": float(row.get("avg_economic_loss") or 0),
                    "avg_refugees_millions": float(row.get("avg_refugees_millions") or 0),
                    "total_refugees_millions": float(row.get("total_refugees_millions") or 0),
                }

                return {"summary": summary, "records": records}

    except Exception as e:
        # Don't pretend there is no data: that makes the AI answer confidently from nothing.
        print(f"[ERROR] Could not read conflict data from the database: {e}")
        raise
