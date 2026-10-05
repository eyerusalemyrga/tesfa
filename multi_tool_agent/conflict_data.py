from psycopg2.extras import RealDictCursor
from multi_tool_agent.tools.db import get_db_connection

def get_conflict_impact_summary(conflict_type: str = None, target_region: str = None) -> dict:
    with get_db_connection() as conn:
        # Use RealDictCursor to safely convert fetched SQL rows to Python dictionaries
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            query = """
                SELECT 
                    COUNT(*) as conflict_count,
                    COALESCE(AVG(civilian_deaths), 0) as avg_civilian_deaths,
                    COALESCE(AVG(military_deaths_a + military_deaths_b), 0) as avg_military_deaths,
                    COALESCE(AVG(economic_loss_usd_billions), 0) as avg_economic_loss,
                    COALESCE(AVG(refugees_millions), 0) as avg_refugees_millions,
                    COALESCE(SUM(refugees_millions), 0) as total_refugees_millions
                FROM tesfa.global_conflicts
                WHERE 1=1
            """
            params = []

            # Flexible match on conflict type
            if conflict_type:
                query += " AND conflict_type ILIKE %s"
                params.append(f"%{conflict_type}%")

            # Flexible match on location across country_a and country_b
            if target_region:
                query += " AND (country_a ILIKE %s OR country_b ILIKE %s)"
                params.extend([f"%{target_region}%", f"%{target_region}%"])

            cur.execute(query, tuple(params))
            row = cur.fetchone()

            # FALLBACK: If combined search finds 0 matching conflicts, query by conflict_type alone
            if row and row.get("conflict_count", 0) == 0 and target_region and conflict_type:
                fallback_query = """
                    SELECT 
                        COUNT(*) as conflict_count,
                        COALESCE(AVG(civilian_deaths), 0) as avg_civilian_deaths,
                        COALESCE(AVG(military_deaths_a + military_deaths_b), 0) as avg_military_deaths,
                        COALESCE(AVG(economic_loss_usd_billions), 0) as avg_economic_loss,
                        COALESCE(AVG(refugees_millions), 0) as avg_refugees_millions,
                        COALESCE(SUM(refugees_millions), 0) as total_refugees_millions
                    FROM tesfa.global_conflicts
                    WHERE conflict_type ILIKE %s;
                """
                cur.execute(fallback_query, (f"%{conflict_type}%",))
                row = cur.fetchone()

            # Return plain dict safely
            return dict(row) if row else {}