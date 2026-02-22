"""Unit tests for the consensus detection engine."""

import pytest

from app.orchestrator.consensus import (
    compute_consensus,
    detect_stagnation,
    score_agreement_markers,
)


class TestAgreementMarkers:
    def test_strong_agreement_scores_high(self):
        responses = [
            "I agree with the previous speaker. Building on that point, education is key.",
            "That's correct, I concur entirely. I share the view that progress is essential.",
        ]
        score = score_agreement_markers(responses)
        assert score > 0.7

    def test_strong_disagreement_scores_low(self):
        responses = [
            "I disagree fundamentally. That overlooks the core issue.",
            "I must counter that. On the contrary, the evidence is insufficient.",
        ]
        score = score_agreement_markers(responses)
        assert score < 0.3

    def test_no_markers_returns_neutral(self):
        responses = [
            "The weather is quite pleasant today.",
            "Mathematics is an interesting subject.",
        ]
        score = score_agreement_markers(responses)
        assert score == 0.5

    def test_mixed_signals_score_moderate(self):
        responses = [
            "I agree that education matters, however I take issue with the scope.",
            "Building on that, I concur partially, but I disagree with the timeline.",
        ]
        score = score_agreement_markers(responses)
        assert 0.2 < score < 0.8

    def test_empty_responses(self):
        score = score_agreement_markers([])
        assert score == 0.5

    def test_single_response(self):
        score = score_agreement_markers(["I agree completely."])
        assert score > 0.5


class TestStagnationDetection:
    def test_identical_content_is_stagnation(self):
        r1 = ["Democracy requires education and informed citizens to function."]
        r2 = ["Democracy requires education and informed citizens to function."]
        assert detect_stagnation(r2, r1) is True

    def test_different_content_not_stagnation(self):
        r1 = ["Democracy requires education and informed citizens."]
        r2 = ["Climate change poses an existential threat to coastal cities."]
        assert detect_stagnation(r2, r1) is False

    def test_first_round_no_stagnation(self):
        r1 = ["Any content at all."]
        assert detect_stagnation(r1, None) is False

    def test_empty_responses(self):
        assert detect_stagnation([], []) is False
        assert detect_stagnation(["something"], []) is False

    def test_similar_but_not_identical(self):
        """Slightly different wording should NOT trigger stagnation (below 80% overlap)."""
        r1 = ["Democracy requires education and informed citizens to function well in society."]
        r2 = ["Democracy requires education and informed citizens to function well in modern society today."]
        result = detect_stagnation(r2, r1)
        # Word overlap is under 80% threshold due to added words, so no stagnation
        assert result is False


class TestComputeConsensus:
    @pytest.mark.asyncio
    async def test_without_llm_returns_valid_score(self):
        transcript = [
            {"speaker": "A", "content": "I agree with B. Building on that excellent point."},
            {"speaker": "B", "content": "I concur with A. That's correct and well-said."},
        ]
        result = await compute_consensus(
            topic="Test",
            round_transcript=transcript,
            previous_round_responses=None,
        )
        assert "consensus_score" in result
        assert 0.0 <= result["consensus_score"] <= 1.0
        assert "marker_score" in result
        assert "stagnation_detected" in result

    @pytest.mark.asyncio
    async def test_disagreement_scores_lower(self):
        agree_transcript = [
            {"speaker": "A", "content": "I agree completely. Well said."},
            {"speaker": "B", "content": "I concur. Exactly right."},
        ]
        disagree_transcript = [
            {"speaker": "A", "content": "I disagree fundamentally. That overlooks everything."},
            {"speaker": "B", "content": "I must counter that. On the contrary."},
        ]
        agree_result = await compute_consensus(
            topic="Test", round_transcript=agree_transcript, previous_round_responses=None
        )
        disagree_result = await compute_consensus(
            topic="Test", round_transcript=disagree_transcript, previous_round_responses=None
        )
        assert agree_result["consensus_score"] > disagree_result["consensus_score"]

    @pytest.mark.asyncio
    async def test_stagnation_penalty_applied(self):
        transcript = [
            {"speaker": "A", "content": "Democracy requires education."},
        ]
        prev = ["Democracy requires education."]
        result = await compute_consensus(
            topic="Test",
            round_transcript=transcript,
            previous_round_responses=prev,
        )
        assert result["stagnation_detected"] is True
