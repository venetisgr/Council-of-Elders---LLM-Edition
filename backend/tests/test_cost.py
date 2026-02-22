"""Unit tests for cost estimation utilities."""

from app.services.cost import estimate_cost, estimate_debate_cost


class TestEstimateCost:
    def test_known_model(self):
        # gpt-4o: $2.50/1M input, $10.00/1M output
        cost = estimate_cost("gpt-4o", input_tokens=1_000_000, output_tokens=1_000_000)
        assert cost == 2.50 + 10.00

    def test_small_token_counts(self):
        cost = estimate_cost("gpt-4o", input_tokens=1000, output_tokens=500)
        expected = (1000 / 1e6) * 2.50 + (500 / 1e6) * 10.00
        assert abs(cost - expected) < 1e-10

    def test_unknown_model_returns_zero(self):
        cost = estimate_cost("nonexistent-model", input_tokens=1000, output_tokens=500)
        assert cost == 0.0

    def test_zero_tokens(self):
        cost = estimate_cost("gpt-4o", input_tokens=0, output_tokens=0)
        assert cost == 0.0

    def test_claude_pricing(self):
        cost = estimate_cost("claude-sonnet-4-6", input_tokens=1_000_000, output_tokens=1_000_000)
        assert cost == 3.0 + 15.0

    def test_gemini_pricing(self):
        cost = estimate_cost("gemini-2.0-flash", input_tokens=1_000_000, output_tokens=1_000_000)
        assert cost == 0.10 + 0.40

    def test_gpt52_pricing(self):
        cost = estimate_cost("gpt-5.2", input_tokens=1_000_000, output_tokens=1_000_000)
        assert cost == 1.75 + 14.0

    def test_deepseek_pricing(self):
        cost = estimate_cost("deepseek-chat", input_tokens=1_000_000, output_tokens=1_000_000)
        assert cost == 0.27 + 1.10

    def test_glm5_pricing(self):
        cost = estimate_cost("glm-5", input_tokens=1_000_000, output_tokens=1_000_000)
        assert cost == 0.80 + 2.56


class TestEstimateDebateCost:
    def test_two_participants(self):
        participants = [
            {"model": "gpt-4o", "display_name": "GPT-4o"},
            {"model": "claude-sonnet-4-6", "display_name": "Claude Sonnet"},
        ]
        estimates = estimate_debate_cost(participants, max_rounds=5)
        assert len(estimates) == 2
        assert "GPT-4o" in estimates
        assert "Claude Sonnet" in estimates
        assert all(v > 0 for v in estimates.values())

    def test_single_round(self):
        participants = [{"model": "gpt-4o", "display_name": "Test"}]
        estimates = estimate_debate_cost(participants, max_rounds=1)
        assert "Test" in estimates
        assert estimates["Test"] > 0

    def test_unknown_model_zero_cost(self):
        participants = [{"model": "unknown", "display_name": "Unknown"}]
        estimates = estimate_debate_cost(participants, max_rounds=10)
        assert estimates["Unknown"] == 0.0

    def test_all_eight_providers(self):
        """Verify cost estimation works for flagship model from each provider."""
        participants = [
            {"model": "claude-opus-4-6", "display_name": "Claude"},
            {"model": "gpt-5.2", "display_name": "GPT"},
            {"model": "gemini-3-pro-preview", "display_name": "Gemini"},
            {"model": "grok-3", "display_name": "Grok"},
            {"model": "deepseek-chat", "display_name": "DeepSeek"},
            {"model": "moonshot-v1-128k", "display_name": "Kimi"},
            {"model": "qwen3-max", "display_name": "Qwen"},
            {"model": "glm-5", "display_name": "GLM"},
        ]
        estimates = estimate_debate_cost(participants, max_rounds=3)
        assert len(estimates) == 8
        assert all(v > 0 for v in estimates.values())
