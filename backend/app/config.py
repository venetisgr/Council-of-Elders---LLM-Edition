"""Application configuration."""

from __future__ import annotations

import os

from pydantic import BaseModel


def _get_cors_origins() -> list[str]:
    """Build CORS origins list from defaults + CORS_ORIGINS env var."""
    defaults = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    extra = os.environ.get("CORS_ORIGINS", "")
    if extra:
        defaults.extend(
            origin.strip() for origin in extra.split(",") if origin.strip()
        )
    return defaults


class AppConfig(BaseModel):
    """Global application settings."""

    app_name: str = "Council of Elders - LLM Edition"
    debug: bool = False
    cors_origins: list[str] = _get_cors_origins()
    session_timeout_seconds: int = 30 * 60  # 30 minutes


config = AppConfig()
