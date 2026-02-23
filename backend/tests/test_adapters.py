"""Unit tests for LLM provider adapters (offline — no API keys needed)."""

import pytest

from app.adapters.base import GenerationConfig, Message, MessageRole
from app.adapters.factory import PROVIDER_MODELS, get_adapter
from app.adapters.anthropic_adapter import AnthropicAdapter, ANTHROPIC_MODELS
from app.adapters.openai_adapter import OpenAIAdapter, OPENAI_MODELS
from app.adapters.gemini_adapter import GeminiAdapter, GEMINI_MODELS
from app.adapters.xai_adapter import XAIAdapter, XAI_BASE_URL, XAI_MODELS
from app.adapters.deepseek_adapter import DeepSeekAdapter, DEEPSEEK_BASE_URL, DEEPSEEK_MODELS
from app.adapters.kimi_adapter import KimiAdapter, KIMI_BASE_URL, KIMI_MODELS
from app.adapters.qwen_adapter import QwenAdapter, QWEN_BASE_URL, QWEN_MODELS
from app.adapters.glm_adapter import GLMAdapter, GLM_BASE_URL, GLM_MODELS

ALL_PROVIDERS = {
    "anthropic", "openai", "google", "xai",
    "deepseek", "kimi", "qwen", "glm",
}


class TestAdapterFactory:
    def test_get_anthropic_adapter(self):
        adapter = get_adapter("anthropic")
        assert isinstance(adapter, AnthropicAdapter)
        assert adapter.provider_name == "anthropic"

    def test_get_openai_adapter(self):
        adapter = get_adapter("openai")
        assert isinstance(adapter, OpenAIAdapter)
        assert adapter.provider_name == "openai"

    def test_get_google_adapter(self):
        adapter = get_adapter("google")
        assert isinstance(adapter, GeminiAdapter)
        assert adapter.provider_name == "google"

    def test_get_xai_adapter(self):
        adapter = get_adapter("xai")
        assert isinstance(adapter, XAIAdapter)
        assert adapter.provider_name == "xai"

    def test_get_deepseek_adapter(self):
        adapter = get_adapter("deepseek")
        assert isinstance(adapter, DeepSeekAdapter)
        assert adapter.provider_name == "deepseek"

    def test_get_kimi_adapter(self):
        adapter = get_adapter("kimi")
        assert isinstance(adapter, KimiAdapter)
        assert adapter.provider_name == "kimi"

    def test_get_qwen_adapter(self):
        adapter = get_adapter("qwen")
        assert isinstance(adapter, QwenAdapter)
        assert adapter.provider_name == "qwen"

    def test_get_glm_adapter(self):
        adapter = get_adapter("glm")
        assert isinstance(adapter, GLMAdapter)
        assert adapter.provider_name == "glm"

    def test_unknown_provider_raises(self):
        with pytest.raises(ValueError, match="Unknown provider"):
            get_adapter("nonexistent")

    def test_all_providers_in_registry(self):
        assert set(PROVIDER_MODELS.keys()) == ALL_PROVIDERS


class TestAnthropicAdapter:
    def test_available_models(self):
        adapter = AnthropicAdapter()
        models = adapter.get_available_models()
        assert len(models) > 0
        assert models == ANTHROPIC_MODELS

    def test_has_opus(self):
        assert "claude-opus-4-6" in ANTHROPIC_MODELS

    def test_has_sonnet(self):
        assert "claude-sonnet-4-6" in ANTHROPIC_MODELS

    def test_prepare_messages_separates_system(self):
        messages = [
            Message(role=MessageRole.SYSTEM, content="You are helpful."),
            Message(role=MessageRole.USER, content="Hello"),
            Message(role=MessageRole.ASSISTANT, content="Hi there"),
        ]
        system, api_msgs = AnthropicAdapter._prepare_messages(messages)
        assert system == "You are helpful."
        assert len(api_msgs) == 2
        assert api_msgs[0]["role"] == "user"
        assert api_msgs[1]["role"] == "assistant"

    def test_prepare_messages_no_system(self):
        messages = [Message(role=MessageRole.USER, content="Hello")]
        system, api_msgs = AnthropicAdapter._prepare_messages(messages)
        assert system == ""
        assert len(api_msgs) == 1


class TestOpenAIAdapter:
    def test_available_models(self):
        adapter = OpenAIAdapter()
        models = adapter.get_available_models()
        assert len(models) > 0
        assert models == OPENAI_MODELS

    def test_has_gpt52(self):
        assert "gpt-5.2" in OPENAI_MODELS

    def test_prepare_messages(self):
        messages = [
            Message(role=MessageRole.SYSTEM, content="Be concise."),
            Message(role=MessageRole.USER, content="Hi"),
        ]
        api_msgs = OpenAIAdapter._prepare_messages(messages)
        assert len(api_msgs) == 2
        assert api_msgs[0] == {"role": "system", "content": "Be concise."}
        assert api_msgs[1] == {"role": "user", "content": "Hi"}

    def test_custom_base_url(self):
        adapter = OpenAIAdapter(base_url="https://custom.api.com/v1")
        assert adapter._base_url == "https://custom.api.com/v1"


class TestXAIAdapter:
    def test_inherits_openai(self):
        adapter = XAIAdapter()
        assert isinstance(adapter, OpenAIAdapter)

    def test_uses_xai_base_url(self):
        adapter = XAIAdapter()
        assert adapter._base_url == XAI_BASE_URL

    def test_available_models(self):
        adapter = XAIAdapter()
        models = adapter.get_available_models()
        assert models == XAI_MODELS
        assert "gpt-4o" not in models

    def test_provider_name(self):
        adapter = XAIAdapter()
        assert adapter.provider_name == "xai"


class TestGeminiAdapter:
    def test_available_models(self):
        adapter = GeminiAdapter()
        models = adapter.get_available_models()
        assert len(models) > 0
        assert models == GEMINI_MODELS

    def test_has_gemini3(self):
        assert "gemini-3-pro-preview" in GEMINI_MODELS

    def test_prepare_messages_separates_system(self):
        messages = [
            Message(role=MessageRole.SYSTEM, content="You are a philosopher."),
            Message(role=MessageRole.USER, content="What is truth?"),
            Message(role=MessageRole.ASSISTANT, content="A complex question."),
        ]
        system, contents = GeminiAdapter._prepare_messages(messages)
        assert system == "You are a philosopher."
        assert len(contents) == 2
        assert contents[0].role == "user"
        assert contents[1].role == "model"

    def test_prepare_messages_no_system(self):
        messages = [Message(role=MessageRole.USER, content="Hello")]
        system, contents = GeminiAdapter._prepare_messages(messages)
        assert system is None
        assert len(contents) == 1


class TestDeepSeekAdapter:
    def test_inherits_openai(self):
        adapter = DeepSeekAdapter()
        assert isinstance(adapter, OpenAIAdapter)

    def test_uses_deepseek_base_url(self):
        adapter = DeepSeekAdapter()
        assert adapter._base_url == DEEPSEEK_BASE_URL

    def test_available_models(self):
        adapter = DeepSeekAdapter()
        models = adapter.get_available_models()
        assert models == DEEPSEEK_MODELS
        assert "deepseek-chat" in models
        assert "deepseek-reasoner" in models

    def test_provider_name(self):
        adapter = DeepSeekAdapter()
        assert adapter.provider_name == "deepseek"


class TestKimiAdapter:
    def test_inherits_openai(self):
        adapter = KimiAdapter()
        assert isinstance(adapter, OpenAIAdapter)

    def test_uses_kimi_base_url(self):
        adapter = KimiAdapter()
        assert adapter._base_url == KIMI_BASE_URL

    def test_available_models(self):
        adapter = KimiAdapter()
        models = adapter.get_available_models()
        assert models == KIMI_MODELS
        assert "moonshot-v1-128k" in models

    def test_provider_name(self):
        adapter = KimiAdapter()
        assert adapter.provider_name == "kimi"


class TestQwenAdapter:
    def test_inherits_openai(self):
        adapter = QwenAdapter()
        assert isinstance(adapter, OpenAIAdapter)

    def test_uses_qwen_base_url(self):
        adapter = QwenAdapter()
        assert adapter._base_url == QWEN_BASE_URL

    def test_available_models(self):
        adapter = QwenAdapter()
        models = adapter.get_available_models()
        assert models == QWEN_MODELS
        assert "qwen3-max" in models

    def test_provider_name(self):
        adapter = QwenAdapter()
        assert adapter.provider_name == "qwen"


class TestGLMAdapter:
    def test_inherits_openai(self):
        adapter = GLMAdapter()
        assert isinstance(adapter, OpenAIAdapter)

    def test_uses_glm_base_url(self):
        adapter = GLMAdapter()
        assert adapter._base_url == GLM_BASE_URL

    def test_available_models(self):
        adapter = GLMAdapter()
        models = adapter.get_available_models()
        assert models == GLM_MODELS
        assert "glm-5" in models

    def test_provider_name(self):
        adapter = GLMAdapter()
        assert adapter.provider_name == "glm"


class TestGenerationConfig:
    def test_defaults(self):
        config = GenerationConfig(model="test-model")
        assert config.max_tokens == 1024
        assert config.temperature == 0.7
        assert config.stop_sequences == []

    def test_custom_values(self):
        config = GenerationConfig(
            model="custom",
            max_tokens=512,
            temperature=0.3,
            stop_sequences=["STOP"],
        )
        assert config.max_tokens == 512
        assert config.temperature == 0.3
        assert config.stop_sequences == ["STOP"]
