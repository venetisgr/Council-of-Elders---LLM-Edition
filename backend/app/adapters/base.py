"""Abstract base class for LLM provider adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncGenerator


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """A message in the conversation history."""

    role: MessageRole
    content: str


@dataclass
class GenerationConfig:
    """Configuration for a single generation call."""

    model: str
    max_tokens: int = 1024
    temperature: float = 0.7
    stop_sequences: list[str] = field(default_factory=list)


@dataclass
class GenerationResult:
    """Metadata returned after a complete generation."""

    content: str
    input_tokens: int = 0
    output_tokens: int = 0
    model: str = ""
    finish_reason: str = ""


class LLMAdapter(ABC):
    """Abstract base class that all LLM provider adapters must implement."""

    provider_name: str = "base"

    @abstractmethod
    async def generate_stream(
        self,
        messages: list[Message],
        config: GenerationConfig,
        api_key: str,
    ) -> AsyncGenerator[str, None]:
        """Stream tokens from the LLM one at a time.

        Args:
            messages: Conversation history including system prompt.
            config: Generation parameters (model, temperature, max_tokens).
            api_key: The user's API key for this provider.

        Yields:
            Individual text tokens/chunks as they arrive.
        """
        ...  # pragma: no cover
        yield ""  # Make this a valid async generator for type checking

    @abstractmethod
    async def generate(
        self,
        messages: list[Message],
        config: GenerationConfig,
        api_key: str,
    ) -> GenerationResult:
        """Generate a complete response (non-streaming).

        Args:
            messages: Conversation history including system prompt.
            config: Generation parameters.
            api_key: The user's API key for this provider.

        Returns:
            GenerationResult with the full response and token usage.
        """
        ...

    @abstractmethod
    async def validate_key(self, api_key: str) -> bool:
        """Check if the provided API key is valid.

        Makes a minimal API call to verify the key works.

        Args:
            api_key: The API key to validate.

        Returns:
            True if the key is valid, False otherwise.
        """
        ...

    @abstractmethod
    def get_available_models(self) -> list[str]:
        """Return the list of model IDs this adapter supports."""
        ...
