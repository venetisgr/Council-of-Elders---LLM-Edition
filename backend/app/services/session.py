"""In-memory session management for debate sessions."""

from __future__ import annotations

import asyncio
import logging
import time

from ..models.debate import DebateSession

logger = logging.getLogger(__name__)

# Session timeout in seconds (30 minutes)
SESSION_TIMEOUT = 30 * 60


class SessionManager:
    """Manages ephemeral debate sessions in memory.

    Sessions are stored in a dict and automatically cleaned up
    after the timeout period. API keys are purged when sessions end.
    """

    def __init__(self):
        self._sessions: dict[str, DebateSession] = {}
        self._last_activity: dict[str, float] = {}
        self._cleanup_task: asyncio.Task | None = None

    def create_session(self, session: DebateSession) -> str:
        """Store a new session and return its ID."""
        self._sessions[session.session_id] = session
        self._last_activity[session.session_id] = time.time()
        logger.info(f"Session created: {session.session_id}")
        return session.session_id

    def get_session(self, session_id: str) -> DebateSession | None:
        """Retrieve a session by ID, updating its last activity time."""
        session = self._sessions.get(session_id)
        if session:
            self._last_activity[session_id] = time.time()
        return session

    def end_session(self, session_id: str) -> None:
        """End a session and purge its API keys from memory."""
        session = self._sessions.pop(session_id, None)
        self._last_activity.pop(session_id, None)
        if session:
            session.api_keys.clear()
            logger.info(f"Session ended and keys purged: {session_id}")

    def list_sessions(self) -> list[str]:
        """Return all active session IDs."""
        return list(self._sessions.keys())

    async def start_cleanup_loop(self) -> None:
        """Start the background cleanup task for expired sessions."""
        self._cleanup_task = asyncio.create_task(self._cleanup_expired())

    async def stop_cleanup_loop(self) -> None:
        """Stop the background cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    async def _cleanup_expired(self) -> None:
        """Periodically remove sessions that have timed out."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                now = time.time()
                expired = [
                    sid
                    for sid, last in self._last_activity.items()
                    if now - last > SESSION_TIMEOUT
                ]
                for sid in expired:
                    logger.info(f"Session expired: {sid}")
                    self.end_session(sid)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Session cleanup error: {e}")


# Global singleton
session_manager = SessionManager()
