"""Pydantic models for provider-related requests and responses."""

from __future__ import annotations

from pydantic import BaseModel

from .debate import Provider


class KeyValidationRequest(BaseModel):
    """Request to validate an API key for a provider."""

    provider: Provider
    api_key: str


class KeyValidationResponse(BaseModel):
    """Response from key validation."""

    provider: Provider
    valid: bool
    message: str = ""
    available_models: list[str] = []
