import json
import uuid
from multi_tool_agent.tools.db import get_db_connection

def create_run(query: str) -> str:
    run_id = str(uuid.uuid4())
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO tesfa.runs (run_id, query) VALUES (%s, %s);", (run_id, query))
                conn.commit()
    except Exception as e:
        print(f"[Log Error] {e}")
    return run_id

def log_step(run_id: str, tool_name: str, input_p: dict, output_p: dict):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO tesfa.steps (run_id, tool_name, input_payload, output_payload) VALUES (%s, %s, %s, %s);",
                    (run_id, tool_name, json.dumps(input_p), json.dumps(output_p))
                )
                conn.commit()
    except Exception as e:
        print(f"[Log Error] {e}")