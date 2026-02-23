"""REST/SSE endpoints for running debates without WebSocket."""

from __future__ import annotations

import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..adapters.base import GenerationConfig, Message, MessageRole
from ..adapters.factory import get_adapter
from ..orchestrator.consensus import compute_consensus
from ..orchestrator.prompts import (
    build_conspectus_prompt,
    build_system_prompt,
    build_turn_prompt,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/debate", tags=["debate"])


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class ParticipantPayload(BaseModel):
    provider: str
    model: str
    display_name: str
    persona: str = ""


class TurnRequest(BaseModel):
    topic: str
    participant: ParticipantPayload
    transcript: list[dict]  # [{"speaker": "...", "content": "..."}]
    api_key: str
    max_tokens: int = 1024
    temperature: float = 0.7


class ConsensusRequest(BaseModel):
    topic: str
    round_transcript: list[dict]
    previous_round_responses: list[str] | None = None
    adapter_provider: str | None = None
    adapter_model: str | None = None
    adapter_api_key: str | None = None


class ConspectusRequest(BaseModel):
    topic: str
    transcript: list[dict]
    participants: list[str]
    rounds: int
    consensus_score: float
    provider: str
    model: str
    api_key: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/turn")
async def debate_turn(request: TurnRequest) -> StreamingResponse:
    """Stream one participant's turn as SSE events."""

    adapter = get_adapter(request.participant.provider)

    system_prompt = build_system_prompt(
        request.participant.display_name,
        request.participant.persona,
    )
    turn_prompt = build_turn_prompt(request.topic, request.transcript)

    messages = [
        Message(role=MessageRole.SYSTEM, content=system_prompt),
        Message(role=MessageRole.USER, content=turn_prompt),
    ]
    config = GenerationConfig(
        model=request.participant.model,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
    )

    async def stream() -> AsyncGenerator[str, None]:
        full_content = ""
        try:
            async for token in adapter.generate_stream(
                messages, config, request.api_key
            ):
                full_content += token
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            token_count = len(full_content.split())
            yield (
                f"data: {json.dumps({'type': 'done', 'content': full_content, 'token_count': token_count})}\n\n"
            )
        except Exception as e:
            logger.error(f"Turn error for {request.participant.display_name}: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@router.post("/consensus")
async def debate_consensus(request: ConsensusRequest) -> dict:
    """Check consensus after a round."""

    adapter = None
    api_key = ""
    model = ""
    if request.adapter_provider and request.adapter_api_key and request.adapter_model:
        adapter = get_adapter(request.adapter_provider)
        api_key = request.adapter_api_key
        model = request.adapter_model

    result = await compute_consensus(
        topic=request.topic,
        round_transcript=request.round_transcript,
        previous_round_responses=request.previous_round_responses,
        adapter=adapter,
        api_key=api_key,
        model=model,
    )
    return result


@router.post("/conspectus")
async def debate_conspectus(request: ConspectusRequest) -> StreamingResponse:
    """Generate the final conspectus, streamed as SSE."""

    adapter = get_adapter(request.provider)

    prompt = build_conspectus_prompt(
        topic=request.topic,
        participants=request.participants,
        rounds=request.rounds,
        consensus_score=request.consensus_score,
        transcript=request.transcript,
    )

    messages = [Message(role=MessageRole.USER, content=prompt)]
    config = GenerationConfig(
        model=request.model,
        max_tokens=2048,
        temperature=0.3,
    )

    async def stream() -> AsyncGenerator[str, None]:
        full_content = ""
        try:
            async for token in adapter.generate_stream(
                messages, config, request.api_key
            ):
                full_content += token
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'content': full_content})}\n\n"
        except Exception as e:
            logger.error(f"Conspectus error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")
