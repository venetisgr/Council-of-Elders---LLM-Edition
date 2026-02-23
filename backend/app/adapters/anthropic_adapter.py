"""Anthropic (Claude) LLM adapter."""

from __future__ import annotations

import logging
from typing import AsyncGenerator

import anthropic

from .base import GenerationConfig, GenerationResult, LLMAdapter, Message, MessageRole

logger = logging.getLogger(__name__)

ANTHROPIC_MODELS = [
    "claude-opus-4-6",
    "claude-sonnet-4-6",
    "claude-haiku-4-5-20251001",
]


class AnthropicAdapter(LLMAdapter):
    """Adapter for Anthropic's Claude models via the Messages API."""

    provider_name = "anthropic"

    async def generate_stream(
        self,
        messages: list[Message],
        config: GenerationConfig,
        api_key: str,
    ) -> AsyncGenerator[str, None]:
        client = anthropic.AsyncAnthropic(api_key=api_key)

        system_prompt, api_messages = self._prepare_messages(messages)

        try:
            async with client.messages.stream(
                model=config.model,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                system=system_prompt,
                messages=api_messages,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except anthropic.AuthenticationError:
            raise ValueError("Invalid Anthropic API key")
        except anthropic.RateLimitError:
            raise RuntimeError("Anthropic rate limit exceeded. Please wait and retry.")
        except anthropic.APIError as e:
            raise RuntimeError(f"Anthropic API error: {e}")

    async def generate(
        self,
        messages: list[Message],
        config: GenerationConfig,
        api_key: str,
    ) -> GenerationResult:
        client = anthropic.AsyncAnthropic(api_key=api_key)

        system_prompt, api_messages = self._prepare_messages(messages)

        try:
            response = await client.messages.create(
                model=config.model,
                max_tokens=config.max_tokens,
                temperature=config.temperature,
                system=system_prompt,
                messages=api_messages,
            )
            return GenerationResult(
                content=response.content[0].text,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                model=response.model,
                finish_reason=response.stop_reason or "",
            )
        except anthropic.AuthenticationError:
            raise ValueError("Invalid Anthropic API key")
        except anthropic.RateLimitError:
            raise RuntimeError("Anthropic rate limit exceeded. Please wait and retry.")
        except anthropic.APIError as e:
            raise RuntimeError(f"Anthropic API error: {e}")

    async def validate_key(self, api_key: str) -> bool:
        client = anthropic.AsyncAnthropic(api_key=api_key)
        try:
            # Minimal call: send a tiny message to verify the key works
            await client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=1,
                messages=[{"role": "user", "content": "hi"}],
            )
            return True
        except anthropic.AuthenticationError:
            return False
        except anthropic.RateLimitError:
            raise RuntimeError("Rate limited. Please wait a moment and try again.")
        except anthropic.APIConnectionError:
            raise RuntimeError(
                "Could not connect to the Anthropic API. "
                "Check your network connection."
            )
        except anthropic.APIError as e:
            raise RuntimeError(f"Anthropic API error: {e.message}")

    def get_available_models(self) -> list[str]:
        return ANTHROPIC_MODELS.copy()

    @staticmethod
    def _prepare_messages(
        messages: list[Message],
    ) -> tuple[str, list[dict]]:
        """Separate system prompt from conversation messages.

        Anthropic requires the system prompt as a separate parameter,
        not in the messages array.
        """
        system_prompt = ""
        api_messages = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_prompt = msg.content
            else:
                api_messages.append({
                    "role": msg.role.value,
                    "content": msg.content,
                })

        return system_prompt, api_messages
