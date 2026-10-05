import json
from pathlib import Path
import anyio

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, model_validator
from multi_tool_agent.main_agent import process_tesfa_query

# Ensure static directory exists before mounting
STATIC_DIR = Path("static")
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Tesfa AI - Post-War Conflict Analytics")

# Mount static folder for serving generated chart images
app.mount("/static", StaticFiles(directory="static"), name="static")


class QueryRequest(BaseModel):
    prompt: str | None = None
    query: str | None = None
    region: str | None = None
    conflict_type: str | None = None

    @model_validator(mode="before")
    @classmethod
    def parse_string_body(cls, values):
        # Automatically parse raw JSON strings if received from clients like Postman
        if isinstance(values, str):
            try:
                return json.loads(values)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON string sent in body")
        return values


@app.post("/api/query")
async def handle_query(req: QueryRequest):
    user_input = req.prompt or req.query
    if not user_input:
        raise HTTPException(
            status_code=422,
            detail="Payload must include either 'prompt' or 'query'.",
        )

    # Offload blocking LLM/RAG calls to a thread pool so Uvicorn stays responsive
    result = await anyio.to_thread.run_sync(
        process_tesfa_query,
        user_input,
        req.region,
        req.conflict_type,
    )
    return result