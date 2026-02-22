"""
Test cases for the Council of Elders backend.

This module contains all test functions organized by component.
It is designed to be imported and run from the Jupyter notebook
(test_backend.ipynb) or executed directly with pytest.

Each test function is async and returns a dict with:
  - "passed": bool
  - "name": str
  - "details": str (human-readable result)
  - "error": str | None

Usage from notebook:
    from test_cases import run_all_tests, run_test_group
    results = await run_all_tests(api_keys={"anthropic": "sk-..."})
    results = await run_test_group("adapters", api_keys={...})
"""

from __future__ import annotations

import json
import sys
import traceback
from dataclasses import dataclass, field
from typing import Callable, Coroutine

# Ensure the backend app is importable
sys.path.insert(0, "..")

from app.adapters.base import GenerationConfig, Message, MessageRole
from app.adapters.factory import PROVIDER_MODELS, get_adapter
from app.models.debate import (
    DebateConfig,
    DebateSession,
    DebateStatus,
    Participant,
    Provider,
)
from app.orchestrator.consensus import (
    compute_consensus,
    detect_stagnation,
    score_agreement_markers,
)
from app.orchestrator.engine import DebateOrchestrator
from app.services.conspectus import generate_conspectus
from app.services.cost import estimate_cost, estimate_debate_cost
from app.services.session import SessionManager

# Default cheap/fast models for testing (to minimize cost)
TEST_MODELS = {
    "anthropic": "claude-haiku-4-20250414",
    "openai": "gpt-4o-mini",
    "google": "gemini-2.0-flash-lite",
    "xai": "grok-3-mini",
}

PROVIDER_TO_ENUM = {
    "anthropic": Provider.ANTHROPIC,
    "openai": Provider.OPENAI,
    "google": Provider.GOOGLE,
    "xai": Provider.XAI,
}


@dataclass
class TestResult:
    name: str
    group: str
    passed: bool
    details: str = ""
    error: str | None = None


@dataclass
class TestSuite:
    results: list[TestResult] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)

    @property
    def total(self) -> int:
        return len(self.results)

    def summary(self) -> str:
        lines = [f"\n{'=' * 60}", f"Test Results: {self.passed}/{self.total} passed\n"]
        for r in self.results:
            icon = "PASS" if r.passed else "FAIL"
            lines.append(f"  [{icon}] {r.group}/{r.name}")
            if r.details:
                lines.append(f"         {r.details}")
            if r.error:
                lines.append(f"         Error: {r.error}")
        lines.append(f"\n{'=' * 60}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# GROUP 1: Adapter Tests (offline — no API keys needed)
# ---------------------------------------------------------------------------


async def test_adapter_factory_valid_providers() -> TestResult:
    """Test that all expected providers return valid adapters."""
    errors = []
    for provider in ["anthropic", "openai", "google", "xai"]:
        try:
            adapter = get_adapter(provider)
            if adapter.provider_name != provider:
                errors.append(f"{provider}: provider_name mismatch ({adapter.provider_name})")
        except Exception as e:
            errors.append(f"{provider}: {e}")

    return TestResult(
        name="adapter_factory_valid_providers",
        group="adapters",
        passed=len(errors) == 0,
        details=f"All 4 providers resolved" if not errors else "; ".join(errors),
    )


async def test_adapter_factory_invalid_provider() -> TestResult:
    """Test that an unknown provider raises ValueError."""
    try:
        get_adapter("nonexistent")
        return TestResult(
            name="adapter_factory_invalid_provider",
            group="adapters",
            passed=False,
            details="Expected ValueError but none raised",
        )
    except ValueError:
        return TestResult(
            name="adapter_factory_invalid_provider",
            group="adapters",
            passed=True,
            details="ValueError raised correctly",
        )


async def test_adapter_available_models() -> TestResult:
    """Test that each adapter returns a non-empty model list."""
    errors = []
    for provider in ["anthropic", "openai", "google", "xai"]:
        adapter = get_adapter(provider)
        models = adapter.get_available_models()
        if not models:
            errors.append(f"{provider}: empty model list")

    return TestResult(
        name="adapter_available_models",
        group="adapters",
        passed=len(errors) == 0,
        details=f"All providers have models" if not errors else "; ".join(errors),
    )


async def test_provider_models_registry() -> TestResult:
    """Test that PROVIDER_MODELS has entries for all providers."""
    expected = {"anthropic", "openai", "google", "xai"}
    actual = set(PROVIDER_MODELS.keys())
    missing = expected - actual
    return TestResult(
        name="provider_models_registry",
        group="adapters",
        passed=len(missing) == 0,
        details=f"All providers registered" if not missing else f"Missing: {missing}",
    )


# ---------------------------------------------------------------------------
# GROUP 2: Adapter Tests (online — require API keys)
# ---------------------------------------------------------------------------


async def test_key_validation(api_keys: dict[str, str]) -> TestResult:
    """Validate API keys for all available providers."""
    results = {}
    for provider, key in api_keys.items():
        if not key:
            continue
        adapter = get_adapter(provider)
        try:
            is_valid = await adapter.validate_key(key)
            results[provider] = "valid" if is_valid else "invalid"
        except Exception as e:
            results[provider] = f"error: {e}"

    all_valid = all(v == "valid" for v in results.values())
    return TestResult(
        name="key_validation",
        group="adapters_online",
        passed=all_valid and len(results) > 0,
        details=str(results) if results else "No keys provided",
    )


async def test_non_streaming_generation(api_keys: dict[str, str]) -> TestResult:
    """Test non-streaming generation for each available provider."""
    messages = [
        Message(role=MessageRole.USER, content="Say 'hello' and nothing else."),
    ]
    results = {}

    for provider, key in api_keys.items():
        if not key:
            continue
        model = TEST_MODELS.get(provider, "")
        adapter = get_adapter(provider)
        config = GenerationConfig(model=model, max_tokens=20, temperature=0.0)
        try:
            result = await adapter.generate(messages, config, key)
            has_content = bool(result.content.strip())
            results[provider] = f"ok ({len(result.content)} chars)" if has_content else "empty response"
        except Exception as e:
            results[provider] = f"error: {e}"

    all_ok = all("ok" in v for v in results.values())
    return TestResult(
        name="non_streaming_generation",
        group="adapters_online",
        passed=all_ok and len(results) > 0,
        details=str(results) if results else "No keys provided",
    )


async def test_streaming_generation(api_keys: dict[str, str]) -> TestResult:
    """Test streaming generation for each available provider."""
    messages = [
        Message(role=MessageRole.USER, content="Say 'hello' and nothing else."),
    ]
    results = {}

    for provider, key in api_keys.items():
        if not key:
            continue
        model = TEST_MODELS.get(provider, "")
        adapter = get_adapter(provider)
        config = GenerationConfig(model=model, max_tokens=20, temperature=0.0)
        try:
            tokens = []
            async for token in adapter.generate_stream(messages, config, key):
                tokens.append(token)
            full = "".join(tokens)
            results[provider] = f"ok ({len(tokens)} chunks, {len(full)} chars)"
        except Exception as e:
            results[provider] = f"error: {e}"

    all_ok = all("ok" in v for v in results.values())
    return TestResult(
        name="streaming_generation",
        group="adapters_online",
        passed=all_ok and len(results) > 0,
        details=str(results) if results else "No keys provided",
    )


# ---------------------------------------------------------------------------
# GROUP 3: Consensus Detection Tests (offline)
# ---------------------------------------------------------------------------


async def test_agreement_markers_high() -> TestResult:
    """Test that strongly agreeing responses score high."""
    responses = [
        "I agree with the previous speaker. Building on that excellent point, education is key.",
        "That's correct, and I concur. I share this view entirely.",
    ]
    score = score_agreement_markers(responses)
    return TestResult(
        name="agreement_markers_high",
        group="consensus",
        passed=score > 0.7,
        details=f"Score: {score:.2f} (expected > 0.7)",
    )


async def test_agreement_markers_low() -> TestResult:
    """Test that strongly disagreeing responses score low."""
    responses = [
        "I disagree fundamentally. That overlooks the core issue entirely.",
        "I must counter that. On the contrary, the evidence is insufficient.",
    ]
    score = score_agreement_markers(responses)
    return TestResult(
        name="agreement_markers_low",
        group="consensus",
        passed=score < 0.3,
        details=f"Score: {score:.2f} (expected < 0.3)",
    )


async def test_agreement_markers_neutral() -> TestResult:
    """Test that neutral/no-marker responses score ~0.5."""
    responses = [
        "The weather is nice today.",
        "Mathematics is the language of nature.",
    ]
    score = score_agreement_markers(responses)
    return TestResult(
        name="agreement_markers_neutral",
        group="consensus",
        passed=0.3 <= score <= 0.7,
        details=f"Score: {score:.2f} (expected ~0.5)",
    )


async def test_stagnation_detection_same() -> TestResult:
    """Test that identical responses trigger stagnation."""
    r1 = ["Democracy requires education and informed citizens to function."]
    r2 = ["Democracy requires education and informed citizens to function."]
    is_stagnant = detect_stagnation(r2, r1)
    return TestResult(
        name="stagnation_detection_same",
        group="consensus",
        passed=is_stagnant,
        details=f"Stagnation detected: {is_stagnant} (expected: True)",
    )


async def test_stagnation_detection_different() -> TestResult:
    """Test that different responses don't trigger stagnation."""
    r1 = ["Democracy requires education and informed citizens."]
    r2 = ["Climate change poses an existential threat to coastal cities."]
    is_stagnant = detect_stagnation(r2, r1)
    return TestResult(
        name="stagnation_detection_different",
        group="consensus",
        passed=not is_stagnant,
        details=f"Stagnation detected: {is_stagnant} (expected: False)",
    )


async def test_stagnation_detection_first_round() -> TestResult:
    """Test that first round (no previous) doesn't trigger stagnation."""
    r1 = ["Any content here."]
    is_stagnant = detect_stagnation(r1, None)
    return TestResult(
        name="stagnation_detection_first_round",
        group="consensus",
        passed=not is_stagnant,
        details=f"Stagnation detected: {is_stagnant} (expected: False)",
    )


async def test_consensus_without_llm() -> TestResult:
    """Test composite consensus scoring without LLM (marker + stagnation only)."""
    transcript = [
        {"speaker": "A", "content": "I agree with B. Building on that point, the evidence supports it."},
        {"speaker": "B", "content": "I concur with A. That's correct and well-said."},
    ]
    result = await compute_consensus(
        topic="Test topic",
        round_transcript=transcript,
        previous_round_responses=None,
        adapter=None,
        api_key="",
        model="",
    )
    score = result["consensus_score"]
    return TestResult(
        name="consensus_without_llm",
        group="consensus",
        passed=0.3 < score < 1.0,
        details=f"Score: {score:.2f}, markers: {result['marker_score']:.2f}",
    )


# ---------------------------------------------------------------------------
# GROUP 4: Session Management Tests (offline)
# ---------------------------------------------------------------------------


async def test_session_create_and_retrieve() -> TestResult:
    """Test creating and retrieving a session."""
    mgr = SessionManager()
    session = DebateSession(
        config=DebateConfig(
            topic="Test",
            participants=[Participant(
                provider=Provider.ANTHROPIC,
                model="test-model",
                display_name="Test",
            )],
        ),
        api_keys={"anthropic": "test-key"},
    )
    sid = mgr.create_session(session)
    retrieved = mgr.get_session(sid)
    return TestResult(
        name="session_create_and_retrieve",
        group="session",
        passed=retrieved is not None and retrieved.config.topic == "Test",
        details=f"Session ID: {sid}",
    )


async def test_session_end_purges_keys() -> TestResult:
    """Test that ending a session purges API keys."""
    mgr = SessionManager()
    session = DebateSession(
        config=DebateConfig(
            topic="Test",
            participants=[Participant(
                provider=Provider.ANTHROPIC,
                model="test-model",
                display_name="Test",
            )],
        ),
        api_keys={"anthropic": "secret-key-123"},
    )
    sid = mgr.create_session(session)
    mgr.end_session(sid)

    keys_empty = len(session.api_keys) == 0
    not_in_manager = mgr.get_session(sid) is None
    return TestResult(
        name="session_end_purges_keys",
        group="session",
        passed=keys_empty and not_in_manager,
        details=f"Keys purged: {keys_empty}, removed from manager: {not_in_manager}",
    )


async def test_session_safe_dict() -> TestResult:
    """Test that to_safe_dict excludes API keys."""
    session = DebateSession(
        config=DebateConfig(
            topic="Test",
            participants=[Participant(
                provider=Provider.ANTHROPIC,
                model="test-model",
                display_name="Test",
            )],
        ),
        api_keys={"anthropic": "secret-key"},
    )
    safe = session.to_safe_dict()
    has_no_keys = "api_keys" not in safe
    return TestResult(
        name="session_safe_dict",
        group="session",
        passed=has_no_keys,
        details=f"api_keys absent from safe dict: {has_no_keys}",
    )


# ---------------------------------------------------------------------------
# GROUP 5: Cost Estimation Tests (offline)
# ---------------------------------------------------------------------------


async def test_cost_estimation_known_model() -> TestResult:
    """Test cost estimation for a known model."""
    cost = estimate_cost("gpt-4o", input_tokens=1000, output_tokens=500)
    expected_approx = (1000 / 1e6) * 2.5 + (500 / 1e6) * 10.0  # ~0.0075
    return TestResult(
        name="cost_estimation_known_model",
        group="cost",
        passed=abs(cost - expected_approx) < 0.001,
        details=f"Cost: ${cost:.6f} (expected ~${expected_approx:.6f})",
    )


async def test_cost_estimation_unknown_model() -> TestResult:
    """Test that unknown models return 0 cost."""
    cost = estimate_cost("nonexistent-model", input_tokens=1000, output_tokens=500)
    return TestResult(
        name="cost_estimation_unknown_model",
        group="cost",
        passed=cost == 0.0,
        details=f"Cost: ${cost:.6f} (expected $0.000000)",
    )


async def test_debate_cost_estimation() -> TestResult:
    """Test pre-debate cost estimation for multiple participants."""
    participants = [
        {"model": "claude-sonnet-4-20250514", "display_name": "Claude Sonnet"},
        {"model": "gpt-4o", "display_name": "GPT-4o"},
    ]
    estimates = estimate_debate_cost(participants, max_rounds=5)
    all_positive = all(v > 0 for v in estimates.values())
    return TestResult(
        name="debate_cost_estimation",
        group="cost",
        passed=all_positive and len(estimates) == 2,
        details=f"Estimates: {estimates}",
    )


# ---------------------------------------------------------------------------
# GROUP 6: Orchestrator Tests (online — requires API keys)
# ---------------------------------------------------------------------------


async def test_mini_debate(api_keys: dict[str, str]) -> TestResult:
    """Run a 1-round mini debate and verify the event flow."""
    available = {k: v for k, v in api_keys.items() if v}
    if len(available) < 1:
        return TestResult(
            name="mini_debate",
            group="orchestrator",
            passed=False,
            details="Need at least 1 API key to run debate test",
        )

    # Build 2 participants (duplicate if only 1 provider)
    participants = []
    keys_for_debate = {}
    for provider, key in available.items():
        keys_for_debate[provider] = key
        model = TEST_MODELS[provider]
        participants.append(Participant(
            provider=PROVIDER_TO_ENUM[provider],
            model=model,
            display_name=f"{provider.title()} Speaker",
        ))
        if len(participants) >= 2:
            break

    if len(participants) < 2:
        # Duplicate the single participant
        dup = participants[0].model_copy()
        dup.display_name = f"{dup.display_name} (2nd)"
        participants.append(dup)

    config = DebateConfig(
        topic="Should pineapple go on pizza?",
        participants=participants,
        max_rounds=1,
        max_tokens_per_turn=100,
        temperature=0.5,
        consensus_threshold=0.99,  # Unlikely to hit in 1 round
    )
    session = DebateSession(config=config, api_keys=keys_for_debate)
    orchestrator = DebateOrchestrator(session)

    events = []
    async for event in orchestrator.run():
        events.append(event.event_type)

    expected_events = {"debate:started", "debate:round_start", "debate:turn_start",
                       "debate:token_stream", "debate:turn_end", "debate:consensus_check",
                       "debate:concluded"}
    actual_events = set(events)
    missing = expected_events - actual_events

    has_transcript = len(session.transcript) >= 2
    is_concluded = session.status == DebateStatus.CONCLUDED

    return TestResult(
        name="mini_debate",
        group="orchestrator",
        passed=len(missing) == 0 and has_transcript and is_concluded,
        details=(
            f"Events: {len(events)} total, transcript: {len(session.transcript)} msgs, "
            f"status: {session.status.value}"
            + (f", missing events: {missing}" if missing else "")
        ),
    )


# ---------------------------------------------------------------------------
# Test Runner
# ---------------------------------------------------------------------------

# All offline (no API key needed) tests
OFFLINE_TESTS: list[Callable[[], Coroutine]] = [
    test_adapter_factory_valid_providers,
    test_adapter_factory_invalid_provider,
    test_adapter_available_models,
    test_provider_models_registry,
    test_agreement_markers_high,
    test_agreement_markers_low,
    test_agreement_markers_neutral,
    test_stagnation_detection_same,
    test_stagnation_detection_different,
    test_stagnation_detection_first_round,
    test_consensus_without_llm,
    test_session_create_and_retrieve,
    test_session_end_purges_keys,
    test_session_safe_dict,
    test_cost_estimation_known_model,
    test_cost_estimation_unknown_model,
    test_debate_cost_estimation,
]

# Online tests (require API keys)
ONLINE_TESTS: list[Callable[[dict], Coroutine]] = [
    test_key_validation,
    test_non_streaming_generation,
    test_streaming_generation,
    test_mini_debate,
]

# Group names for selective running
TEST_GROUPS = {
    "adapters": [
        test_adapter_factory_valid_providers,
        test_adapter_factory_invalid_provider,
        test_adapter_available_models,
        test_provider_models_registry,
    ],
    "adapters_online": [
        test_key_validation,
        test_non_streaming_generation,
        test_streaming_generation,
    ],
    "consensus": [
        test_agreement_markers_high,
        test_agreement_markers_low,
        test_agreement_markers_neutral,
        test_stagnation_detection_same,
        test_stagnation_detection_different,
        test_stagnation_detection_first_round,
        test_consensus_without_llm,
    ],
    "session": [
        test_session_create_and_retrieve,
        test_session_end_purges_keys,
        test_session_safe_dict,
    ],
    "cost": [
        test_cost_estimation_known_model,
        test_cost_estimation_unknown_model,
        test_debate_cost_estimation,
    ],
    "orchestrator": [
        test_mini_debate,
    ],
}


async def run_all_tests(api_keys: dict[str, str] | None = None) -> TestSuite:
    """Run all tests (offline + online if keys provided).

    Args:
        api_keys: Dict of provider -> API key. Online tests run only for
                  providers that have non-empty keys.

    Returns:
        TestSuite with all results.
    """
    suite = TestSuite()
    api_keys = api_keys or {}

    # Run offline tests
    for test_fn in OFFLINE_TESTS:
        try:
            result = await test_fn()
            suite.results.append(result)
        except Exception as e:
            suite.results.append(TestResult(
                name=test_fn.__name__,
                group="unknown",
                passed=False,
                error=f"{type(e).__name__}: {e}",
            ))

    # Run online tests (if any keys provided)
    available = {k: v for k, v in api_keys.items() if v}
    if available:
        for test_fn in ONLINE_TESTS:
            try:
                result = await test_fn(api_keys)
                suite.results.append(result)
            except Exception as e:
                suite.results.append(TestResult(
                    name=test_fn.__name__,
                    group="unknown",
                    passed=False,
                    error=f"{type(e).__name__}: {e}\n{traceback.format_exc()}",
                ))

    return suite


async def run_test_group(
    group: str, api_keys: dict[str, str] | None = None
) -> TestSuite:
    """Run tests for a specific group.

    Args:
        group: One of "adapters", "adapters_online", "consensus",
               "session", "cost", "orchestrator".
        api_keys: Required for online groups.

    Returns:
        TestSuite with results for the specified group.
    """
    suite = TestSuite()
    tests = TEST_GROUPS.get(group, [])
    api_keys = api_keys or {}

    for test_fn in tests:
        try:
            # Check if the test requires api_keys parameter
            import inspect
            sig = inspect.signature(test_fn)
            if "api_keys" in sig.parameters:
                result = await test_fn(api_keys)
            else:
                result = await test_fn()
            suite.results.append(result)
        except Exception as e:
            suite.results.append(TestResult(
                name=test_fn.__name__,
                group=group,
                passed=False,
                error=f"{type(e).__name__}: {e}",
            ))

    return suite
