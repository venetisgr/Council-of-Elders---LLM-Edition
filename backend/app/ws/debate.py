"""WebSocket event handlers for debate sessions."""

from __future__ import annotations

import logging

import socketio

from ..models.debate import (
    DebateConfig,
    DebateSession,
    DebateStatus,
    Participant,
    Provider,
)
from ..orchestrator.engine import DebateOrchestrator
from ..services.conspectus import generate_conspectus
from ..services.session import session_manager

logger = logging.getLogger(__name__)

# Active orchestrators keyed by session_id
_orchestrators: dict[str, DebateOrchestrator] = {}


def register_debate_events(sio: socketio.AsyncServer) -> None:
    """Register all debate-related WebSocket event handlers."""

    @sio.event
    async def connect(sid: str, environ: dict) -> None:
        logger.info(f"Client connected: {sid}")

    @sio.event
    async def disconnect(sid: str) -> None:
        logger.info(f"Client disconnected: {sid}")

    @sio.on("debate:start")
    async def handle_debate_start(sid: str, data: dict) -> None:
        """Start a new debate session.

        Expected data:
        {
            "topic": "...",
            "participants": [
                {"provider": "anthropic", "model": "claude-sonnet-4-20250514", "display_name": "Claude Sonnet", "persona": ""},
                ...
            ],
            "api_keys": {"anthropic": "sk-...", "openai": "sk-...", ...},
            "max_rounds": 10,
            "max_tokens_per_turn": 1024,
            "temperature": 0.7,
            "consensus_threshold": 0.8
        }
        """
        try:
            participants = [
                Participant(
                    provider=Provider(p["provider"]),
                    model=p["model"],
                    display_name=p["display_name"],
                    persona=p.get("persona", ""),
                )
                for p in data.get("participants", [])
            ]

            config = DebateConfig(
                topic=data["topic"],
                participants=participants,
                max_rounds=data.get("max_rounds", 10),
                max_tokens_per_turn=data.get("max_tokens_per_turn", 1024),
                temperature=data.get("temperature", 0.7),
                consensus_threshold=data.get("consensus_threshold", 0.8),
            )

            session = DebateSession(
                config=config,
                api_keys=data.get("api_keys", {}),
            )
            session_manager.create_session(session)

            # Put client in a room for this session
            sio.enter_room(sid, session.session_id)

            orchestrator = DebateOrchestrator(session)
            _orchestrators[session.session_id] = orchestrator

            # Run the debate and emit events
            async for event in orchestrator.run():
                await sio.emit(
                    event.event_type,
                    event.data,
                    room=session.session_id,
                )

            # Generate conspectus after debate concludes
            if session.status == DebateStatus.CONCLUDED:
                await sio.emit(
                    "debate:generating_conspectus",
                    {"session_id": session.session_id},
                    room=session.session_id,
                )
                conspectus = await generate_conspectus(session)
                session.conspectus = conspectus
                await sio.emit(
                    "debate:conspectus",
                    {
                        "session_id": session.session_id,
                        "conspectus": conspectus,
                    },
                    room=session.session_id,
                )

            # Cleanup
            _orchestrators.pop(session.session_id, None)
            session_manager.end_session(session.session_id)

        except Exception as e:
            logger.error(f"Debate start error: {e}")
            await sio.emit("debate:error", {"error": str(e)}, to=sid)

    @sio.on("debate:pause")
    async def handle_debate_pause(sid: str, data: dict) -> None:
        """Pause an ongoing debate."""
        session_id = data.get("session_id", "")
        orchestrator = _orchestrators.get(session_id)
        if orchestrator:
            orchestrator.pause()
            await sio.emit(
                "debate:paused",
                {"session_id": session_id},
                room=session_id,
            )

    @sio.on("debate:resume")
    async def handle_debate_resume(sid: str, data: dict) -> None:
        """Resume a paused debate."""
        session_id = data.get("session_id", "")
        orchestrator = _orchestrators.get(session_id)
        if orchestrator:
            orchestrator.resume()
            await sio.emit(
                "debate:resumed",
                {"session_id": session_id},
                room=session_id,
            )

    @sio.on("debate:stop")
    async def handle_debate_stop(sid: str, data: dict) -> None:
        """Stop a debate early."""
        session_id = data.get("session_id", "")
        orchestrator = _orchestrators.get(session_id)
        if orchestrator:
            orchestrator.stop()
            await sio.emit(
                "debate:stopped",
                {"session_id": session_id},
                room=session_id,
            )
