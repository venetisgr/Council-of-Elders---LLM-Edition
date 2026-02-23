"""Pytest configuration and shared fixtures."""

import pytest


@pytest.fixture
def sample_api_keys():
    """Fake API keys for testing (not valid for real API calls)."""
    return {
        "anthropic": "sk-ant-test-fake-key",
        "openai": "sk-test-fake-key",
        "google": "AIza-test-fake-key",
        "xai": "xai-test-fake-key",
    }
