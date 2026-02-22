"""Unit tests for prompt templates."""

from app.orchestrator.prompts import (
    build_conspectus_prompt,
    build_consensus_prompt,
    build_system_prompt,
    build_turn_prompt,
)


class TestBuildSystemPrompt:
    def test_includes_display_name(self):
        prompt = build_system_prompt("Claude Opus")
        assert "Claude Opus" in prompt

    def test_includes_persona_when_provided(self):
        prompt = build_system_prompt("Claude", persona="Argue in favor of democracy")
        assert "Argue in favor of democracy" in prompt

    def test_no_persona_section_when_empty(self):
        prompt = build_system_prompt("Claude", persona="")
        assert "Your assigned perspective" not in prompt

    def test_includes_agora_rules(self):
        prompt = build_system_prompt("Test")
        assert "Agora" in prompt
        assert "intellectual honesty" in prompt


class TestBuildTurnPrompt:
    def test_first_speaker_no_transcript(self):
        prompt = build_turn_prompt("Is democracy good?", [])
        assert "Is democracy good?" in prompt
        assert "first to speak" in prompt

    def test_includes_transcript(self):
        transcript = [
            {"speaker": "Claude", "content": "Democracy enables freedom."},
            {"speaker": "GPT", "content": "But it can lead to tyranny of the majority."},
        ]
        prompt = build_turn_prompt("Is democracy good?", transcript)
        assert "Claude" in prompt
        assert "Democracy enables freedom" in prompt
        assert "GPT" in prompt
        assert "tyranny of the majority" in prompt


class TestBuildConsensusPrompt:
    def test_includes_topic_and_transcript(self):
        transcript = [
            {"speaker": "A", "content": "I believe X."},
            {"speaker": "B", "content": "I agree with X."},
        ]
        prompt = build_consensus_prompt("Test topic", transcript)
        assert "Test topic" in prompt
        assert "I believe X" in prompt
        assert "I agree with X" in prompt
        assert "JSON" in prompt


class TestBuildConspectusPrompt:
    def test_includes_all_fields(self):
        transcript = [
            {"speaker": "A", "content": "Point one.", "round": 1},
            {"speaker": "B", "content": "Point two.", "round": 1},
        ]
        prompt = build_conspectus_prompt(
            topic="Test topic",
            participants=["A", "B"],
            rounds=3,
            consensus_score=0.75,
            transcript=transcript,
        )
        assert "Test topic" in prompt
        assert "A, B" in prompt
        assert "3" in prompt
        assert "75%" in prompt
        assert "Point one" in prompt
        assert "Synthesis" in prompt
