"""OpenAI (GPT) LLM adapter."""

from __future__ import annotations

import logging
from typing import AsyncGenerator

import openai

from .base import GenerationConfig, GenerationResult, LLMAdapter, Message

logger = logging.getLogger(__name__)

OPENAI_MODELS = [
    "gpt-5.2",
    "gpt-4o",
    "gpt-4o-mini",
]


class OpenAIAdapter(LLMAdapter):
    """Adapter for OpenAI's GPT models via the Chat Completions API."""

    provider_name = "openai"
    # Newer OpenAI models (GPT-5.2, o-series) require 'max_completion_tokens'
    # instead of 'max_tokens'. Third-party OpenAI-compatible providers that
    # don't yet support this parameter can override with "max_tokens".
    _token_limit_param = "max_completion_tokens"

    def __init__(self, base_url: str | None = None):
        """Initialize with optional custom base URL (used by xAI adapter)."""
        self._base_url = base_url

    async def generate_stream(
        self,
        messages: list[Message],
        config: GenerationConfig,
        api_key: str,
    ) -> AsyncGenerator[str, None]:
        client = openai.AsyncOpenAI(api_key=api_key, base_url=self._base_url)
        api_messages = self._prepare_messages(messages)

        try:
            stream = await client.chat.completions.create(
                model=config.model,
                messages=api_messages,
                temperature=config.temperature,
                stream=True,
                **{self._token_limit_param: config.max_tokens},
            )
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except openai.AuthenticationError:
            raise ValueError("Invalid OpenAI API key")
        except openai.NotFoundError:
            raise RuntimeError(
                f"Model '{config.model}' was not found or is not a chat model. "
                "Please check the model name and try a different one."
            )
        except openai.RateLimitError:
            raise RuntimeError("OpenAI rate limit exceeded. Please wait and retry.")
        except openai.APIError as e:
            raise RuntimeError(f"OpenAI API error: {e}")

    async def generate(
        self,
        messages: list[Message],
        config: GenerationConfig,
        api_key: str,
    ) -> GenerationResult:
        client = openai.AsyncOpenAI(api_key=api_key, base_url=self._base_url)
        api_messages = self._prepare_messages(messages)

        try:
            response = await client.chat.completions.create(
                model=config.model,
                messages=api_messages,
                temperature=config.temperature,
                **{self._token_limit_param: config.max_tokens},
            )
            choice = response.choices[0]
            return GenerationResult(
                content=choice.message.content or "",
                input_tokens=response.usage.prompt_tokens if response.usage else 0,
                output_tokens=response.usage.completion_tokens if response.usage else 0,
                model=response.model,
                finish_reason=choice.finish_reason or "",
            )
        except openai.AuthenticationError:
            raise ValueError("Invalid OpenAI API key")
        except openai.NotFoundError:
            raise RuntimeError(
                f"Model '{config.model}' was not found or is not a chat model. "
                "Please check the model name and try a different one."
            )
        except openai.RateLimitError:
            raise RuntimeError("OpenAI rate limit exceeded. Please wait and retry.")
        except openai.APIError as e:
            raise RuntimeError(f"OpenAI API error: {e}")

    async def validate_key(self, api_key: str) -> bool:
        client = openai.AsyncOpenAI(api_key=api_key, base_url=self._base_url)
        try:
            await client.models.list()
            return True
        except openai.AuthenticationError:
            return False
        except openai.RateLimitError:
            raise RuntimeError("Rate limited. Please wait a moment and try again.")
        except openai.APIConnectionError:
            raise RuntimeError(
                f"Could not connect to the {self.provider_name} API. "
                "Check your network connection."
            )
        except openai.APIError as e:
            raise RuntimeError(f"API error from {self.provider_name}: {e.message}")

    def get_available_models(self) -> list[str]:
        return OPENAI_MODELS.copy()

    @staticmethod
    def _prepare_messages(messages: list[Message]) -> list[dict]:
        """Convert our Message objects to OpenAI's format."""
        return [{"role": msg.role.value, "content": msg.content} for msg in messages]
