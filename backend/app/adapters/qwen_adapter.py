"""Qwen (Alibaba Cloud) LLM adapter — uses OpenAI-compatible API.

Placeholder: adapter structure is ready, model IDs and base URL
may need updating as Alibaba evolves their API.
"""

from __future__ import annotations

from .openai_adapter import OpenAIAdapter

# International endpoint; use https://dashscope.aliyuncs.com/compatible-mode/v1
# for China mainland.
QWEN_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

QWEN_MODELS = [
    "qwen3-max",
    "qwen3.5-plus",
    "qwen-plus",
]


class QwenAdapter(OpenAIAdapter):
    """Adapter for Alibaba Qwen models via DashScope.

    Alibaba's DashScope provides an OpenAI-compatible API, so this adapter
    inherits from OpenAIAdapter and overrides the base URL and model list.
    """

    provider_name = "qwen"

    def __init__(self):
        super().__init__(base_url=QWEN_BASE_URL)

    def get_available_models(self) -> list[str]:
        return QWEN_MODELS.copy()
