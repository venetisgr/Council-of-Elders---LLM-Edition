"""Pydantic models for debate sessions, messages, and configuration."""

from __future__ import annotations

import uuid
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class Provider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    XAI = "xai"


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class DebateMessage(BaseModel):
    """A single message in the debate transcript."""

    speaker: str  # Display name, e.g. "Claude Opus", "GPT-4o"
    provider: Provider
    model: str  # Specific model ID, e.g. "claude-sonnet-4-20250514"
    role: MessageRole = MessageRole.ASSISTANT
    content: str = ""
    round_number: int
    token_count: int = 0


class Participant(BaseModel):
    """An LLM participant in the debate."""

    provider: Provider
    model: str
    display_name: str
    persona: str = ""  # Optional role/perspective assignment


class DebateConfig(BaseModel):
    """Configuration for a debate session."""

    topic: str
    participants: list[Participant]
    max_rounds: int = Field(default=10, ge=1, le=50)
    max_tokens_per_turn: int = Field(default=1024, ge=100, le=4096)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    consensus_threshold: float = Field(default=0.8, ge=0.0, le=1.0)


class DebateStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    CONCLUDED = "concluded"
    ERROR = "error"


class ConsensusResult(BaseModel):
    """Result of a consensus check after a round."""

    score: float = Field(ge=0.0, le=1.0)
    agreement_markers: dict[str, float] = Field(default_factory=dict)
    stagnation_detected: bool = False
    summary: str = ""


class DebateSession(BaseModel):
    """Full state of a debate session."""

    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    config: DebateConfig
    status: DebateStatus = DebateStatus.PENDING
    current_round: int = 0
    transcript: list[DebateMessage] = Field(default_factory=list)
    consensus_history: list[ConsensusResult] = Field(default_factory=list)
    api_keys: dict[str, str] = Field(default_factory=dict)  # provider -> key
    conspectus: str = ""
    token_usage: dict[str, int] = Field(default_factory=dict)  # speaker -> total tokens

    model_config = ConfigDict(json_encoders={})

    def to_safe_dict(self) -> dict:
        """Serialize without API keys."""
        data = self.model_dump()
        data.pop("api_keys", None)
        return data
