"""FastAPI application entry point with Socket.IO integration."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.debate import router as debate_router
from .api.keys import router as keys_router
from .config import config
from .services.session import session_manager
from .ws.debate import register_debate_events

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info(f"Starting {config.app_name}")
    await session_manager.start_cleanup_loop()
    yield
    logger.info("Shutting down...")
    await session_manager.stop_cleanup_loop()


# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=config.cors_origins,
)

# Register WebSocket event handlers
register_debate_events(sio)

# Create FastAPI app
app = FastAPI(
    title=config.app_name,
    description="Multi-LLM debate platform — the Athenian Agora for AI",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST API routers
app.include_router(keys_router)
app.include_router(debate_router)


# Health check
@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "app": config.app_name}


# Mount Socket.IO as an ASGI sub-application
socket_app = socketio.ASGIApp(sio, other_app=app)
