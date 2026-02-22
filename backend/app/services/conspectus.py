"""Conspectus (summary) generation service."""

from __future__ import annotations

import logging

from ..adapters.base import GenerationConfig, Message, MessageRole
from ..adapters.factory import get_adapter
from ..models.debate import DebateSession
from ..orchestrator.prompts import build_conspectus_prompt

logger = logging.getLogger(__name__)


async def generate_conspectus(session: DebateSession) -> str:
    """Generate a conspectus (structured summary) of the completed debate.

    Uses the first available LLM adapter to produce the summary.

    Args:
        session: The completed debate session with full transcript.

    Returns:
        The conspectus as a markdown string.
    """
    # Find an available adapter + key
    adapter = None
    api_key = ""
    model = ""
    for participant in session.config.participants:
        key = session.api_keys.get(participant.provider.value)
        if key:
            adapter = get_adapter(participant.provider.value)
            api_key = key
            model = participant.model
            break

    if not adapter or not api_key:
        return "Unable to generate conspectus: no available LLM adapter."

    # Build the transcript
    transcript_entries = [
        {
            "speaker": msg.speaker,
            "content": msg.content,
            "round": msg.round_number,
        }
        for msg in session.transcript
    ]

    participants = [p.display_name for p in session.config.participants]
    final_score = (
        session.consensus_history[-1].score
        if session.consensus_history
        else 0.0
    )

    prompt = build_conspectus_prompt(
        topic=session.config.topic,
        participants=participants,
        rounds=session.current_round,
        consensus_score=final_score,
        transcript=transcript_entries,
    )

    messages = [
        Message(role=MessageRole.USER, content=prompt),
    ]
    config = GenerationConfig(
        model=model,
        max_tokens=2048,
        temperature=0.3,  # Low temperature for factual summary
    )

    try:
        result = await adapter.generate(messages, config, api_key)
        return result.content
    except Exception as e:
        logger.error(f"Conspectus generation failed: {e}")
        return f"Conspectus generation failed: {e}"
