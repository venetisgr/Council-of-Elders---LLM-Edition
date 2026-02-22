"""Kimi (Moonshot AI) LLM adapter — uses OpenAI-compatible API.

Placeholder: adapter structure is ready, model IDs and base URL
may need updating as Moonshot evolves their API.
"""

from __future__ import annotations

from .openai_adapter import OpenAIAdapter

KIMI_BASE_URL = "https://api.moonshot.cn/v1"

KIMI_MODELS = [
    "moonshot-v1-128k",
    "moonshot-v1-32k",
    "moonshot-v1-8k",
]


class KimiAdapter(OpenAIAdapter):
    """Adapter for Kimi / Moonshot AI models.

    Moonshot provides an OpenAI-compatible API, so this adapter inherits
    from OpenAIAdapter and overrides the base URL and model list.
    """

    provider_name = "kimi"

    def __init__(self):
        super().__init__(base_url=KIMI_BASE_URL)

    def get_available_models(self) -> list[str]:
        return KIMI_MODELS.copy()
