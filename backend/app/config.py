"""Application configuration."""

from __future__ import annotations

from pydantic import BaseModel


class AppConfig(BaseModel):
    """Global application settings."""

    app_name: str = "Council of Elders - LLM Edition"
    debug: bool = False
    cors_origins: list[str] = [
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    session_timeout_seconds: int = 30 * 60  # 30 minutes


config = AppConfig()
