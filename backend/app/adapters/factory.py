"""Factory for creating LLM adapters by provider name."""

from __future__ import annotations

from .anthropic_adapter import ANTHROPIC_MODELS, AnthropicAdapter
from .base import LLMAdapter
from .gemini_adapter import GEMINI_MODELS, GeminiAdapter
from .openai_adapter import OPENAI_MODELS, OpenAIAdapter
from .xai_adapter import XAI_MODELS, XAIAdapter

# Map of provider -> list of supported models
PROVIDER_MODELS: dict[str, list[str]] = {
    "anthropic": ANTHROPIC_MODELS,
    "openai": OPENAI_MODELS,
    "google": GEMINI_MODELS,
    "xai": XAI_MODELS,
}

_ADAPTER_REGISTRY: dict[str, type[LLMAdapter]] = {
    "anthropic": AnthropicAdapter,
    "openai": OpenAIAdapter,
    "google": GeminiAdapter,
    "xai": XAIAdapter,
}


def get_adapter(provider: str) -> LLMAdapter:
    """Get an LLM adapter instance for the given provider.

    Args:
        provider: Provider name (anthropic, openai, google, xai).

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
