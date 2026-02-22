"""xAI (Grok) LLM adapter — uses OpenAI-compatible API."""

from __future__ import annotations

from .openai_adapter import OpenAIAdapter

XAI_BASE_URL = "https://api.x.ai/v1"

XAI_MODELS = [
    "grok-3",
    "grok-3-mini",
    "grok-2",
    "grok-2-mini",
]


class XAIAdapter(OpenAIAdapter):
    """Adapter for xAI's Grok models.

    xAI provides an OpenAI-compatible API, so this adapter inherits
    from OpenAIAdapter and just overrides the base URL and model list.
    """

    provider_name = "xai"

    def __init__(self):
        super().__init__(base_url=XAI_BASE_URL)

    def get_available_models(self) -> list[str]:
        return XAI_MODELS.copy()
