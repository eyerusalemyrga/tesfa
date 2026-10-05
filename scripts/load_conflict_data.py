import os
import sys
import pandas as pd
from multi_tool_agent.tools.db import get_db_connection
from multi_tool_agent.rag import index_document_chunk
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
def init_db_schema():
    """Create necessary database extension and tables."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
           
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute("CREATE SCHEMA IF NOT EXISTS tesfa;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tesfa.global_conflicts (
                    id SERIAL PRIMARY KEY,
                    country_a VARCHAR(100),
                    country_b VARCHAR(100),
                    conflict_type VARCHAR(100),
                    year INT,
                    duration_days INT,
                    military_deaths_a INT,
                    military_deaths_b INT,
                    civilian_deaths INT,
                    economic_loss_usd_billions FLOAT,
                    refugees_millions FLOAT,
                    weapons_used VARCHAR(100),
                    ceasefire VARCHAR(10),
                    outcome VARCHAR(100),
                    un_involvement VARCHAR(10),
                    sanctions VARCHAR(10)
                );
            """)

            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tesfa.rag_embeddings (
                    id SERIAL PRIMARY KEY,
                    document_title VARCHAR(255),
                    content_chunk TEXT,
                    embedding vector(768),
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

           
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tesfa.runs (
                    run_id VARCHAR(100) PRIMARY KEY,
                    query TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tesfa.steps (
                    id SERIAL PRIMARY KEY,
                    run_id VARCHAR(100) REFERENCES tesfa.runs(run_id),
                    tool_name VARCHAR(100),
                    input_payload JSONB,
                    output_payload JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
    print("Database schema initialized successfully.")

def load_csv_to_postgres(csv_path="global_conflicts_dataset.csv"):
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found in root directory.")
        return

    df = pd.read_csv(csv_path)

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for _, row in df.iterrows():
                cur.execute(
                    """
                    INSERT INTO tesfa.global_conflicts 
                    (country_a, country_b, conflict_type, year, duration_days, 
                     military_deaths_a, military_deaths_b, civilian_deaths, 
                     economic_loss_usd_billions, refugees_millions, weapons_used, 
                     ceasefire, outcome, un_involvement, sanctions)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        row['Country_A'], row['Country_B'], row['Conflict_Type'], int(row['Year']), int(row['Duration_Days']),
                        int(row['Military_Deaths_A']), int(row['Military_Deaths_B']), int(row['Civilian_Deaths']),
                        float(row['Economic_Loss_USD_Billions']), float(row['Refugees_Millions']), row['Weapons_Used'],
                        row['Ceasefire'], row['Outcome'], row['UN_Involvement'], row['Sanctions']
                    )
                )
            conn.commit()

    print(f"Loaded {len(df)} records into PostgreSQL table 'tesfa.global_conflicts'.")

    
    try:
        index_document_chunk(
            title="Global Conflicts Dataset Analysis",
            content="Post-conflict analysis indicates that conflicts generate significant human displacement and civilian casualties.",
            metadata={"source": "global_conflicts_dataset.csv"}
        )
        print("Vector index chunk generated successfully.")
    except Exception as e:
        print(f"Warning: Vector indexing failed (check GEMINI_API_KEY): {e}")

if __name__ == "__main__":
    init_db_schema()
    load_csv_to_postgres()