import uuid

from psycopg2.extras import Json

from multi_tool_agent.tools.db import get_db_connection


def record_run(query: str, tool_name: str, input_payload: dict, output_payload: dict) -> None:
    """Save one question and its outcome (tesfa.runs + tesfa.steps) in a single transaction.

    Logging must never break an answer, so any failure is printed and swallowed.
    """
    run_id = str(uuid.uuid4())
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO tesfa.runs (run_id, query) VALUES (%s, %s)", (run_id, query))
                cur.execute(
                    "INSERT INTO tesfa.steps (run_id, tool_name, input_payload, output_payload) "
                    "VALUES (%s, %s, %s, %s)",
                    (run_id, tool_name, Json(input_payload), Json(output_payload)),
                )
            conn.commit()
    except Exception as e:
        print(f"[Log Error] {e}")
