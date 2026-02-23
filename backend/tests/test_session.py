"""Unit tests for session management."""

from app.models.debate import (
    DebateConfig,
    DebateSession,
    Participant,
    Provider,
)
from app.services.session import SessionManager


def _make_session(**kwargs) -> DebateSession:
    """Helper to create a test session."""
    defaults = dict(
        config=DebateConfig(
            topic="Test topic",
            participants=[
                Participant(
                    provider=Provider.ANTHROPIC,
                    model="test-model",
                    display_name="Test Speaker",
                ),
                Participant(
                    provider=Provider.OPENAI,
                    model="test-model-2",
                    display_name="Test Speaker 2",
                ),
            ],
        ),
        api_keys={"anthropic": "test-key-12345"},
    )
    defaults.update(kwargs)
    return DebateSession(**defaults)


class TestSessionManager:
    def test_create_and_retrieve(self):
        mgr = SessionManager()
        session = _make_session()
        sid = mgr.create_session(session)

        retrieved = mgr.get_session(sid)
        assert retrieved is not None
        assert retrieved.session_id == sid
        assert retrieved.config.topic == "Test topic"

    def test_retrieve_nonexistent_returns_none(self):
        mgr = SessionManager()
        assert mgr.get_session("nonexistent-id") is None

    def test_end_session_removes_it(self):
        mgr = SessionManager()
        session = _make_session()
        sid = mgr.create_session(session)

        mgr.end_session(sid)
        assert mgr.get_session(sid) is None

    def test_end_session_purges_keys(self):
        mgr = SessionManager()
        session = _make_session(api_keys={"anthropic": "secret-key"})
        sid = mgr.create_session(session)

        mgr.end_session(sid)
        assert len(session.api_keys) == 0

    def test_list_sessions(self):
        mgr = SessionManager()
        s1 = _make_session()
        s2 = _make_session()
        mgr.create_session(s1)
        mgr.create_session(s2)

        sessions = mgr.list_sessions()
        assert len(sessions) == 2
        assert s1.session_id in sessions
        assert s2.session_id in sessions

    def test_end_nonexistent_session_no_error(self):
        mgr = SessionManager()
        mgr.end_session("nonexistent")  # Should not raise


class TestDebateSession:
    def test_to_safe_dict_excludes_keys(self):
        session = _make_session(api_keys={"anthropic": "secret"})
        safe = session.to_safe_dict()
        assert "api_keys" not in safe
        assert safe["config"]["topic"] == "Test topic"

    def test_default_status_is_pending(self):
        session = _make_session()
        assert session.status.value == "pending"

    def test_session_id_generated(self):
        s1 = _make_session()
        s2 = _make_session()
        assert s1.session_id != s2.session_id
        assert len(s1.session_id) > 0
