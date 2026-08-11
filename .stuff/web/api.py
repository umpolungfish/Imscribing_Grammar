"""
web/api.py — Imscribing Grammar Oracle API

FastAPI backend for the public inquiry interface.
Wraps TrueAgenticAgent behind a single POST /inquire endpoint.

Required env var: GROQ_API_KEY
Optional env var: IG_ORACLE_MODEL (default: groq:llama-3.3-70b-versatile)
                  IG_ORACLE_ORIGIN (CORS origin to allow, default: *)

Deploy: fly.io (see fly.toml at project root)
"""
from __future__ import annotations

import asyncio
import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from agents.true_agentic_agent import TrueAgenticAgent

# ── Config ────────────────────────────────────────────────────────────────────

MODEL  = os.environ.get("IG_MODEL") or os.environ.get("IG_ORACLE_MODEL", "groq:llama-3.3-70b-versatile")
ORIGIN = os.environ.get("IG_ORACLE_ORIGIN", "*")
MAX_TASK_CHARS = 2000
MAX_WINDINGS   = 20

app = FastAPI(title="IG Oracle", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ORIGIN],
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type"],
    max_age=600,
)

# ── Models ────────────────────────────────────────────────────────────────────

class InquiryRequest(BaseModel):
    task: str

    @field_validator("task")
    @classmethod
    def task_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("task cannot be empty")
        if len(v) > MAX_TASK_CHARS:
            raise ValueError(f"task exceeds {MAX_TASK_CHARS} characters")
        return v

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok", "model": MODEL}


@app.post("/inquire")
async def inquire(req: InquiryRequest) -> JSONResponse:
    groq_key = os.environ.get("GROQ_API_KEY", "")
    if MODEL.startswith("groq:") and not groq_key:
        raise HTTPException(status_code=503, detail="Oracle not configured — GROQ_API_KEY absent")

    t0 = time.monotonic()
    try:
        agent = TrueAgenticAgent(
            model=MODEL,
            max_windings=MAX_WINDINGS,
            verbose=False,
        )
        result = await agent.run(req.task)
        st = agent.structural_type
        elapsed = round(time.monotonic() - t0, 1)

        return JSONResponse({
            "ok": True,
            "result":          result,
            "tier":            st.get("ouroboricity", ""),
            "frobenius":       round(float(st.get("frobenius_ratio", 0)), 3),
            "windings":        st.get("windings", 0),
            "done":            st.get("done", False),
            "elapsed_s":       elapsed,
        })

    except SystemExit as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Oracle timed out — try a simpler inquiry")
    except Exception as exc:
        return JSONResponse(status_code=500, content={
            "ok": False,
            "error": str(exc),
        })


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web.api:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), reload=False)
