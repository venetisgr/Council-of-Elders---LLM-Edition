"""GLM (Zhipu AI) LLM adapter — uses OpenAI-compatible API.

Placeholder: adapter structure is ready, model IDs and base URL
may need updating as Zhipu evolves their API.
"""

from __future__ import annotations

from .openai_adapter import OpenAIAdapter

GLM_BASE_URL = "https://open.bigmodel.cn/api/paas/v4"

GLM_MODELS = [
    "glm-5",
    "glm-4-plus",
]


class GLMAdapter(OpenAIAdapter):
    """Adapter for Zhipu AI GLM models.

    Zhipu provides an OpenAI-compatible API, so this adapter inherits
    from OpenAIAdapter and overrides the base URL and model list.
    """

    provider_name = "glm"

    def __init__(self):
        super().__init__(base_url=GLM_BASE_URL)

    def get_available_models(self) -> list[str]:
        return GLM_MODELS.copy()
