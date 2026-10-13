import asyncio
import json
import traceback
from pathlib import Path
import anyio

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, model_validator
from multi_tool_agent.llm import LLMUnavailableError
from multi_tool_agent.main_agent import process_tesfa_query

STATIC_DIR = Path("static")
STATIC_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Tesfa AI - Post-War Conflict Analytics")
app.mount("/static", StaticFiles(directory="static"), name="static")


class QueryRequest(BaseModel):
    prompt: str | None = None
    query: str | None = None
    region: str | None = None
    conflict_type: str | None = None

    @model_validator(mode="before")
    @classmethod
    def parse_string_body(cls, values):
        if isinstance(values, str):
            try:
                return json.loads(values)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON string sent in body")
        return values


@app.get("/")
async def root():
    return {
        "service": "Tesfa AI - Post-War Conflict & Environmental Analysis",
        "version": "1.0",
        "endpoints": {
            "POST /api/query": "Submit a conflict analysis query",
            "GET /health": "Health check",
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Tesfa"}


@app.post("/api/query")
async def handle_query(req: QueryRequest):
    user_input = req.prompt or req.query
    if not user_input:
        raise HTTPException(
            status_code=422,
            detail="Payload must include either 'prompt' or 'query'.",
        )

    print(f"\n[INFO] Starting processing for query: '{user_input}'")

    try:
        # Wrap the offloaded thread execution with standard asyncio.wait_for timeout
        result = await asyncio.wait_for(
            anyio.to_thread.run_sync(
                process_tesfa_query,
                user_input,
                req.region,
                req.conflict_type,
            ),
            timeout=90.0,
        )
        print("[INFO] Query completed successfully.")
        inner = result.get("result", {})
        if set(inner) <= {"status", "analysis_text"}:
            return PlainTextResponse(inner.get("analysis_text", "") + "\n")
        return result

    except asyncio.TimeoutError:
        print("[ERROR] Request timed out after 90 seconds.")
        raise HTTPException(
            status_code=504,
            detail="Request timed out. External API or Database is not responding.",
        )
    except LLMUnavailableError as e:
        print(f"[ERROR] AI service unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail="The AI service is busy right now. Please try again in a moment.",
        )
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Something went wrong on our side.")
