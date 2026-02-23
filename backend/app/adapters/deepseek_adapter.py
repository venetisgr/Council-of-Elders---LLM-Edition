"""DeepSeek LLM adapter — uses OpenAI-compatible API."""

from __future__ import annotations

from .openai_adapter import OpenAIAdapter

DEEPSEEK_BASE_URL = "https://api.deepseek.com"

DEEPSEEK_MODELS = [
    "deepseek-chat",
    "deepseek-reasoner",
]


class DeepSeekAdapter(OpenAIAdapter):
    """Adapter for DeepSeek models.

    DeepSeek provides an OpenAI-compatible API, so this adapter inherits
    from OpenAIAdapter and overrides the base URL and model list.
    """

    provider_name = "deepseek"
    _token_limit_param = "max_tokens"

    def __init__(self):
        super().__init__(base_url=DEEPSEEK_BASE_URL)

    def get_available_models(self) -> list[str]:
        return DEEPSEEK_MODELS.copy()
