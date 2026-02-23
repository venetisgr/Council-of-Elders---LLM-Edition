"""Debate orchestrator — the core engine that runs debates."""

from __future__ import annotations

import logging
from typing import AsyncGenerator

from ..adapters.base import GenerationConfig, Message, MessageRole
from ..adapters.factory import get_adapter
from ..models.debate import (
    ConsensusResult,
    DebateConfig,
    DebateMessage,
    DebateSession,
    DebateStatus,
    Participant,
)
from .consensus import compute_consensus
from .prompts import build_system_prompt, build_turn_prompt

logger = logging.getLogger(__name__)


class DebateEvent:
    """Events emitted during the debate."""

    def __init__(self, event_type: str, data: dict):
        self.event_type = event_type
        self.data = data

    def __repr__(self) -> str:
        return f"DebateEvent({self.event_type}, {self.data})"


class DebateOrchestrator:
    """Orchestrates a multi-LLM debate with structured rounds."""

    def __init__(self, session: DebateSession):
        self.session = session
        self._paused = False
        self._stopped = False

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def stop(self) -> None:
        self._stopped = True

    async def run(self) -> AsyncGenerator[DebateEvent, None]:
        """Run the debate, yielding events as they occur.

        This is the main entry point for the debate. It manages rounds,
        speaker turns, consensus checks, and termination.

        Yields:
            DebateEvent objects for each significant state change.
        """
        self.session.status = DebateStatus.RUNNING
        yield DebateEvent("debate:started", {
            "session_id": self.session.session_id,
            "topic": self.session.config.topic,
            "participants": [p.display_name for p in self.session.config.participants],
        })

        previous_round_responses: list[str] | None = None
        stagnation_count = 0

        for round_num in range(1, self.session.config.max_rounds + 1):
            if self._stopped:
                break

            self.session.current_round = round_num
            yield DebateEvent("debate:round_start", {"round": round_num})

            round_responses: list[str] = []
            round_transcript: list[dict] = []

            # Each participant takes a turn (round-robin)
            for participant in self.session.config.participants:
                if self._stopped:
                    break

                # Wait while paused
                while self._paused and not self._stopped:
                    import asyncio
                    await asyncio.sleep(0.5)

                if self._stopped:
                    break

                yield DebateEvent("debate:turn_start", {
                    "speaker": participant.display_name,
                    "provider": participant.provider.value,
                    "round": round_num,
                })

                try:
                    full_response = ""
                    async for token in self._generate_turn(participant, round_num):
                        full_response += token
                        yield DebateEvent("debate:token_stream", {
                            "speaker": participant.display_name,
                            "token": token,
                        })

                    # Record the message
                    message = DebateMessage(
                        speaker=participant.display_name,
                        provider=participant.provider,
                        model=participant.model,
                        content=full_response,
                        round_number=round_num,
                        token_count=len(full_response.split()),  # Rough estimate
                    )
                    self.session.transcript.append(message)
                    round_responses.append(full_response)
                    round_transcript.append({
                        "speaker": participant.display_name,
                        "content": full_response,
                        "round": round_num,
                    })

                    # Track token usage
                    key = participant.display_name
                    self.session.token_usage[key] = (
                        self.session.token_usage.get(key, 0) + message.token_count
                    )

                    yield DebateEvent("debate:turn_end", {
                        "speaker": participant.display_name,
                        "round": round_num,
                        "token_count": message.token_count,
                    })

                except Exception as e:
                    logger.error(
                        f"Error during {participant.display_name}'s turn: {e}"
                    )
                    yield DebateEvent("debate:error", {
                        "speaker": participant.display_name,
                        "error": str(e),
                        "round": round_num,
                    })
                    # Skip this speaker and continue with next
                    continue

            if self._stopped:
                break

            # Consensus check after each round
            consensus_result = await self._check_consensus(
                round_transcript, previous_round_responses
            )

            self.session.consensus_history.append(ConsensusResult(
                score=consensus_result["consensus_score"],
                stagnation_detected=consensus_result["stagnation_detected"],
                summary=consensus_result.get("summary", ""),
            ))

            yield DebateEvent("debate:consensus_check", {
                "round": round_num,
                "consensus_score": consensus_result["consensus_score"],
                "stagnation_detected": consensus_result["stagnation_detected"],
                "agreed_points": consensus_result.get("agreed_points", []),
                "contested_points": consensus_result.get("contested_points", []),
                "summary": consensus_result.get("summary", ""),
            })

            # Check termination conditions
            if consensus_result["consensus_score"] >= self.session.config.consensus_threshold:
                yield DebateEvent("debate:consensus_reached", {
                    "round": round_num,
                    "score": consensus_result["consensus_score"],
                })
                break

            if consensus_result["stagnation_detected"]:
                stagnation_count += 1
                if stagnation_count >= 3:
                    yield DebateEvent("debate:stagnation", {
                        "round": round_num,
                        "consecutive_stagnation_rounds": stagnation_count,
                    })
                    break
            else:
                stagnation_count = 0

            previous_round_responses = round_responses

        # Debate concluded
        self.session.status = DebateStatus.CONCLUDED
        yield DebateEvent("debate:concluded", {
            "session_id": self.session.session_id,
            "total_rounds": self.session.current_round,
            "final_consensus": (
                self.session.consensus_history[-1].score
                if self.session.consensus_history
                else 0.0
            ),
            "token_usage": self.session.token_usage,
        })

    async def _generate_turn(
        self, participant: Participant, round_num: int
    ) -> AsyncGenerator[str, None]:
        """Generate a single speaker's response for the current turn."""
        adapter = get_adapter(participant.provider.value)
        api_key = self.session.api_keys.get(participant.provider.value, "")

        if not api_key:
            raise ValueError(
                f"No API key provided for {participant.provider.value}"
            )

        # Build the conversation messages
        system_prompt = build_system_prompt(
            participant.display_name, participant.persona
        )

        # Build transcript for context
        transcript_entries = [
            {"speaker": msg.speaker, "content": msg.content}
            for msg in self.session.transcript
        ]
        turn_prompt = build_turn_prompt(
            self.session.config.topic, transcript_entries
        )

        messages = [
            Message(role=MessageRole.SYSTEM, content=system_prompt),
            Message(role=MessageRole.USER, content=turn_prompt),
        ]

        config = GenerationConfig(
            model=participant.model,
            max_tokens=self.session.config.max_tokens_per_turn,
            temperature=participant.temperature,
        )

        async for token in adapter.generate_stream(messages, config, api_key):
            yield token

    async def _check_consensus(
        self,
        round_transcript: list[dict],
        previous_round_responses: list[str] | None,
    ) -> dict:
        """Run consensus detection after a round.

        Uses the first available adapter + key for LLM-based consensus analysis.
        Falls back to marker-based analysis if no adapter is available.
        """
        # Find the first available adapter+key for consensus analysis
        adapter = None
        api_key = ""
        model = ""
        for participant in self.session.config.participants:
            key = self.session.api_keys.get(participant.provider.value)
            if key:
                adapter = get_adapter(participant.provider.value)
                api_key = key
                model = participant.model
                break

        return await compute_consensus(
            topic=self.session.config.topic,
            round_transcript=round_transcript,
            previous_round_responses=previous_round_responses,
            adapter=adapter,
            api_key=api_key,
            model=model,
        )
