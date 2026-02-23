"""Vercel serverless API — key validation and provider listing.

This is a lightweight FastAPI app that reuses the existing backend
adapter code for LLM key validation.  It does NOT import Socket.IO,
the session manager, or the debate orchestrator — only the stateless
REST endpoints needed for the setup phase.
"""

import os
import sys

# Make backend package importable so `from app.…` resolves
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from app.api.keys import router as keys_router  # noqa: E402

app = FastAPI(title="Council of Elders API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# /api/keys/validate  and  /api/keys/providers
app.include_router(keys_router)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "app": "Council of Elders - LLM Edition"}
