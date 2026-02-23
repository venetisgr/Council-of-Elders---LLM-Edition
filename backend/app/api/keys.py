"""API key validation endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from ..adapters.factory import PROVIDER_MODELS, get_adapter
from ..models.providers import KeyValidationRequest, KeyValidationResponse

router = APIRouter(prefix="/api/keys", tags=["keys"])


@router.post("/validate", response_model=KeyValidationResponse)
async def validate_key(request: KeyValidationRequest) -> KeyValidationResponse:
    """Validate an API key for a given provider.

    Makes a minimal API call to verify the key is functional.
    The key is NOT stored — it's used only for this validation call.
    """
    try:
        adapter = get_adapter(request.provider.value)
    except ValueError as e:
        return KeyValidationResponse(
            provider=request.provider,
            valid=False,
            message=str(e),
        )

    try:
        is_valid = await adapter.validate_key(request.api_key)
    except RuntimeError as e:
        # Non-auth failures (network, rate limit, API errors)
        return KeyValidationResponse(
            provider=request.provider,
            valid=False,
            message=str(e),
        )

    if is_valid:
        return KeyValidationResponse(
            provider=request.provider,
            valid=True,
            message="API key is valid.",
            available_models=PROVIDER_MODELS.get(request.provider.value, []),
        )
    else:
        return KeyValidationResponse(
            provider=request.provider,
            valid=False,
            message="Invalid API key. Please check your key and try again.",
        )


@router.get("/providers")
async def list_providers() -> dict:
    """List all supported providers and their available models."""
    return {"providers": PROVIDER_MODELS}
