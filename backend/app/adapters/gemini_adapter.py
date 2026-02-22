"""Google Gemini LLM adapter."""

from __future__ import annotations

import logging
from typing import AsyncGenerator

from google import genai
from google.genai import types

from .base import GenerationConfig, GenerationResult, LLMAdapter, Message, MessageRole

logger = logging.getLogger(__name__)

GEMINI_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
]


class GeminiAdapter(LLMAdapter):
    """Adapter for Google's Gemini models via the Google GenAI SDK."""

    provider_name = "google"

    async def generate_stream(
        self,
        messages: list[Message],
        config: GenerationConfig,
        api_key: str,
    ) -> AsyncGenerator[str, None]:
        client = genai.Client(api_key=api_key)
        system_instruction, contents = self._prepare_messages(messages)

        try:
            response = client.models.generate_content_stream(
                model=config.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    max_output_tokens=config.max_tokens,
                    temperature=config.temperature,
                ),
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            error_str = str(e).lower()
            if "api key" in error_str or "permission" in error_str or "403" in error_str:
                raise ValueError("Invalid Google API key")
            elif "quota" in error_str or "429" in error_str:
                raise RuntimeError("Google API rate limit exceeded. Please wait and retry.")
            else:
                raise RuntimeError(f"Google API error: {e}")

    async def generate(
        self,
        messages: list[Message],
        config: GenerationConfig,
        api_key: str,
    ) -> GenerationResult:
        client = genai.Client(api_key=api_key)
        system_instruction, contents = self._prepare_messages(messages)

        try:
            response = client.models.generate_content(
                model=config.model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    max_output_tokens=config.max_tokens,
                    temperature=config.temperature,
                ),
            )
            usage = response.usage_metadata
            return GenerationResult(
                content=response.text or "",
                input_tokens=usage.prompt_token_count if usage else 0,
                output_tokens=usage.candidates_token_count if usage else 0,
                model=config.model,
                finish_reason="stop",
            )
        except Exception as e:
            error_str = str(e).lower()
            if "api key" in error_str or "permission" in error_str or "403" in error_str:
                raise ValueError("Invalid Google API key")
            elif "quota" in error_str or "429" in error_str:
                raise RuntimeError("Google API rate limit exceeded. Please wait and retry.")
            else:
                raise RuntimeError(f"Google API error: {e}")

    async def validate_key(self, api_key: str) -> bool:
        client = genai.Client(api_key=api_key)
        try:
            # Minimal call to verify the key
            client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents="hi",
                config=types.GenerateContentConfig(max_output_tokens=1),
            )
            return True
        except Exception as e:
            logger.warning(f"Google key validation failed: {e}")
            return False

    def get_available_models(self) -> list[str]:
        return GEMINI_MODELS.copy()

    @staticmethod
    def _prepare_messages(
        messages: list[Message],
    ) -> tuple[str | None, list[types.Content]]:
        """Convert messages to Gemini's format.

        Gemini uses 'user' and 'model' roles (not 'assistant'),
        and system instructions are passed separately.
        """
        system_instruction = None
        contents: list[types.Content] = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_instruction = msg.content
            else:
                role = "model" if msg.role == MessageRole.ASSISTANT else "user"
                contents.append(
                    types.Content(
                        role=role,
                        parts=[types.Part(text=msg.content)],
                    )
                )

        return system_instruction, contents
