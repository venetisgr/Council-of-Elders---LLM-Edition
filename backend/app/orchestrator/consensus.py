"""Consensus detection engine for debates."""

from __future__ import annotations

import json
import logging
import re

from ..adapters.base import GenerationConfig, LLMAdapter, Message, MessageRole
from .prompts import build_consensus_prompt

logger = logging.getLogger(__name__)

# Phrases that signal agreement or disagreement
AGREEMENT_MARKERS = [
    "i agree",
    "i concur",
    "that's correct",
    "building on",
    "exactly right",
    "well said",
    "i share",
    "common ground",
    "we seem to converge",
    "as .* correctly pointed out",
    "aligns with my view",
    "i must acknowledge",
]

DISAGREEMENT_MARKERS = [
    "i disagree",
    "i must counter",
    "however",
    "on the contrary",
    "that misses",
    "i take issue",
    "fundamentally flawed",
    "i challenge",
    "that overlooks",
    "insufficient",
]


def score_agreement_markers(responses: list[str]) -> float:
    """Score agreement vs disagreement from explicit markers in responses.

    Returns a score from 0.0 (all disagreement) to 1.0 (all agreement).
    """
    agreement_count = 0
    disagreement_count = 0

    for response in responses:
        text = response.lower()
        for marker in AGREEMENT_MARKERS:
            agreement_count += len(re.findall(marker, text))
        for marker in DISAGREEMENT_MARKERS:
            disagreement_count += len(re.findall(marker, text))

    total = agreement_count + disagreement_count
    if total == 0:
        return 0.5  # Neutral if no markers found

    return agreement_count / total


def detect_stagnation(
    current_round_responses: list[str],
    previous_round_responses: list[str] | None,
) -> bool:
    """Detect if the debate is stagnating (same arguments repeated).

    Uses a simple word overlap heuristic between consecutive rounds.
    """
    if not previous_round_responses:
        return False

    current_words = set()
    for r in current_round_responses:
        current_words.update(r.lower().split())

    previous_words = set()
    for r in previous_round_responses:
        previous_words.update(r.lower().split())

    if not current_words or not previous_words:
        return False

    overlap = len(current_words & previous_words) / max(
        len(current_words | previous_words), 1
    )
    # If > 80% word overlap, likely stagnating
    return overlap > 0.8


async def evaluate_consensus_with_llm(
    topic: str,
    round_transcript: list[dict],
    adapter: LLMAdapter,
    api_key: str,
    model: str,
) -> dict:
    """Use an LLM to evaluate the consensus state.

    Returns a dict with consensus_score, agreed_points, contested_points,
    stagnation, and summary.
    """
    prompt = build_consensus_prompt(topic, round_transcript)
    messages = [
        Message(role=MessageRole.USER, content=prompt),
    ]
    config = GenerationConfig(
        model=model,
        max_tokens=512,
        temperature=0.1,  # Low temperature for analytical task
    )

    try:
        result = await adapter.generate(messages, config, api_key)
        # Parse JSON from response
        json_match = re.search(r"\{.*\}", result.content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        logger.warning(f"LLM consensus evaluation failed: {e}")

    # Fallback: return neutral result
    return {
        "consensus_score": 0.5,
        "agreed_points": [],
        "contested_points": [],
        "stagnation": False,
        "summary": "Unable to evaluate consensus.",
    }


async def compute_consensus(
    topic: str,
    round_transcript: list[dict],
    previous_round_responses: list[str] | None,
    adapter: LLMAdapter | None = None,
    api_key: str = "",
    model: str = "",
) -> dict:
    """Compute the composite consensus score using multiple signals.

    Combines:
    - Signal 1: Explicit agreement markers (weight: 0.3)
    - Signal 2: LLM-based position analysis (weight: 0.5)
    - Signal 3: Stagnation penalty (weight: 0.2)

    Returns a dict with the composite score and analysis.
    """
    current_responses = [entry["content"] for entry in round_transcript]

    # Signal 1: Agreement markers
    marker_score = score_agreement_markers(current_responses)

    # Signal 2: LLM-based analysis (if adapter available)
    llm_analysis = None
    llm_score = 0.5
    if adapter and api_key and model:
        llm_analysis = await evaluate_consensus_with_llm(
            topic, round_transcript, adapter, api_key, model
        )
        llm_score = llm_analysis.get("consensus_score", 0.5)

    # Signal 3: Stagnation
    stagnation = detect_stagnation(current_responses, previous_round_responses)
    stagnation_penalty = 0.3 if stagnation else 0.0

    # Composite score
    w1, w2, w3 = 0.3, 0.5, 0.2
    composite = (
        w1 * marker_score
        + w2 * llm_score
        + w3 * (1.0 - stagnation_penalty)
    )
    composite = max(0.0, min(1.0, composite))

    return {
        "consensus_score": composite,
        "marker_score": marker_score,
        "llm_score": llm_score,
        "stagnation_detected": stagnation,
        "agreed_points": llm_analysis.get("agreed_points", []) if llm_analysis else [],
        "contested_points": llm_analysis.get("contested_points", []) if llm_analysis else [],
        "summary": llm_analysis.get("summary", "") if llm_analysis else "",
    }
