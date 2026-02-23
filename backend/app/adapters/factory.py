"""Factory for creating LLM adapters by provider name."""

from __future__ import annotations

from .anthropic_adapter import ANTHROPIC_MODELS, AnthropicAdapter
from .base import LLMAdapter
from .deepseek_adapter import DEEPSEEK_MODELS, DeepSeekAdapter
from .gemini_adapter import GEMINI_MODELS, GeminiAdapter
from .glm_adapter import GLM_MODELS, GLMAdapter
from .kimi_adapter import KIMI_MODELS, KimiAdapter
from .openai_adapter import OPENAI_MODELS, OpenAIAdapter
from .qwen_adapter import QWEN_MODELS, QwenAdapter
from .xai_adapter import XAI_MODELS, XAIAdapter

# Map of provider -> list of supported models
PROVIDER_MODELS: dict[str, list[str]] = {
    "anthropic": ANTHROPIC_MODELS,
    "openai": OPENAI_MODELS,
    "google": GEMINI_MODELS,
    "xai": XAI_MODELS,
    "deepseek": DEEPSEEK_MODELS,
    "kimi": KIMI_MODELS,
    "qwen": QWEN_MODELS,
    "glm": GLM_MODELS,
}

_ADAPTER_REGISTRY: dict[str, type[LLMAdapter]] = {
    "anthropic": AnthropicAdapter,
    "openai": OpenAIAdapter,
    "google": GeminiAdapter,
    "xai": XAIAdapter,
    "deepseek": DeepSeekAdapter,
    "kimi": KimiAdapter,
    "qwen": QwenAdapter,
    "glm": GLMAdapter,
}


def get_adapter(provider: str) -> LLMAdapter:
    """Get an LLM adapter instance for the given provider.

    Args:
        provider: Provider name (anthropic, openai, google, xai,
                  deepseek, kimi, qwen, glm).

    Returns:
        An instance of the appropriate LLMAdapter subclass.

    Raises:
        ValueError: If the provider is not supported.
    """
    adapter_cls = _ADAPTER_REGISTRY.get(provider)
    if adapter_cls is None:
        supported = ", ".join(_ADAPTER_REGISTRY.keys())
        raise ValueError(f"Unknown provider '{provider}'. Supported: {supported}")
    return adapter_cls()
