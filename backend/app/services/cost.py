"""Token usage and cost estimation utilities."""

from __future__ import annotations

# Approximate pricing per 1M tokens (input/output) in USD as of early 2026.
# These are rough estimates — actual pricing varies by model.
PRICING: dict[str, dict[str, float]] = {
    # Anthropic
    "claude-opus-4-6": {"input": 15.0, "output": 75.0},
    "claude-sonnet-4-6": {"input": 3.0, "output": 15.0},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.0},
    # OpenAI
    "gpt-5.2": {"input": 1.75, "output": 14.0},
    "gpt-5.2-pro": {"input": 15.0, "output": 60.0},
    "gpt-4o": {"input": 2.50, "output": 10.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "o3-mini": {"input": 1.10, "output": 4.40},
    # Google
    "gemini-3-pro-preview": {"input": 1.25, "output": 10.0},
    "gemini-2.5-pro-preview-06-05": {"input": 1.25, "output": 10.0},
    "gemini-2.0-flash": {"input": 0.10, "output": 0.40},
    "gemini-2.0-flash-lite": {"input": 0.075, "output": 0.30},
    # xAI
    "grok-3": {"input": 3.0, "output": 15.0},
    "grok-3-mini": {"input": 0.30, "output": 0.50},
    "grok-2": {"input": 2.0, "output": 10.0},
    "grok-2-mini": {"input": 0.30, "output": 0.50},
    # DeepSeek
    "deepseek-chat": {"input": 0.27, "output": 1.10},
    "deepseek-reasoner": {"input": 0.55, "output": 2.19},
    # Kimi (Moonshot) — approximate
    "moonshot-v1-128k": {"input": 0.84, "output": 0.84},
    "moonshot-v1-32k": {"input": 0.34, "output": 0.34},
    "moonshot-v1-8k": {"input": 0.17, "output": 0.17},
    # Qwen (Alibaba) — approximate
    "qwen3-max": {"input": 1.60, "output": 6.40},
    "qwen3.5-plus": {"input": 0.80, "output": 3.20},
    "qwen-plus": {"input": 0.80, "output": 3.20},
    # GLM (Zhipu) — approximate
    "glm-5": {"input": 0.80, "output": 2.56},
    "glm-4-plus": {"input": 0.70, "output": 0.70},
}


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """Estimate the cost for a given model and token counts.

    Returns cost in USD. Returns 0.0 if the model is not in the pricing table.
    """
    pricing = PRICING.get(model)
    if not pricing:
        return 0.0

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost


def estimate_debate_cost(
    participants: list[dict],
    max_rounds: int,
    avg_input_tokens: int = 2000,
    avg_output_tokens: int = 500,
) -> dict[str, float]:
    """Estimate the total cost of a debate before it starts.

    Args:
        participants: List of dicts with 'model' and 'display_name' keys.
        max_rounds: Maximum number of debate rounds.
        avg_input_tokens: Estimated average input tokens per turn.
        avg_output_tokens: Estimated average output tokens per turn.

    Returns:
        Dict mapping participant display_name to estimated cost in USD.
    """
    estimates = {}
    for p in participants:
        model = p["model"]
        turns = max_rounds  # Each participant speaks once per round
        total_input = avg_input_tokens * turns
        total_output = avg_output_tokens * turns
        estimates[p["display_name"]] = estimate_cost(model, total_input, total_output)
    return estimates
