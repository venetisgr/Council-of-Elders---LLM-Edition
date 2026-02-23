"""Prompt templates for the debate orchestrator."""

SPEAKER_SYSTEM_PROMPT = """\
You are {display_name}, participating in a philosophical debate at the Agora — \
a forum where great minds deliberate on important questions.

{persona_section}

Rules of the Agora:
- Engage directly with the specific points raised by other speakers
- Be substantive: support your arguments with reasoning, evidence, or examples
- If you agree with a point made by another speaker, say so explicitly and build upon it
- If you disagree, explain precisely why and offer a counter-argument
- Aim for intellectual honesty and depth over winning
- Be concise but thorough — respect the assembly's time
- When you find common ground with others, acknowledge it clearly\
"""

SPEAKER_TURN_PROMPT = """\
Topic for deliberation: {topic}

{transcript_section}

It is now your turn to address the assembly. Respond to the arguments above, \
advancing the discourse toward deeper understanding.\
"""

CONSENSUS_EXTRACTION_PROMPT = """\
You are an impartial observer at the Agora. Analyze the latest round of debate \
and assess the degree of consensus among the speakers.

Topic: {topic}

Latest round transcript:
{round_transcript}

Respond with a JSON object (and nothing else) containing:
{{
  "consensus_score": <float 0.0-1.0, where 1.0 = complete agreement>,
  "agreed_points": [<list of points where speakers agree>],
  "contested_points": [<list of points where speakers disagree>],
  "stagnation": <true if the arguments are repetitive and not advancing, false otherwise>,
  "summary": "<one sentence summary of the current state of the debate>"
}}\
"""

CONSPECTUS_PROMPT = """\
You are a neutral scribe at the Athenian Agora. The debate on the following \
topic has concluded after {rounds} rounds. Produce a conspectus — a comprehensive \
summary that synthesizes the deliberation.

Topic: {topic}
Participants: {participants}
Final consensus score: {consensus_score:.0%}

Full transcript:
{transcript}

Write a structured conspectus with these sections:

## Overview
What was debated and why it matters.

## Key Arguments
The strongest arguments from each participant, attributed by name.

## Points of Agreement
Where the speakers converged — the shared understanding that emerged.

## Remaining Disagreements
Where positions remain divergent, and why.

## Synthesis
The final conspectus: what can we conclude from this deliberation? \
What wisdom did the assembly produce together?\
"""


def build_system_prompt(display_name: str, persona: str = "") -> str:
    """Build the system prompt for a debate participant."""
    persona_section = ""
    if persona:
        persona_section = f"Your assigned perspective: {persona}\n"

    return SPEAKER_SYSTEM_PROMPT.format(
        display_name=display_name,
        persona_section=persona_section,
    )


def build_turn_prompt(topic: str, transcript: list[dict]) -> str:
    """Build the user prompt for a speaker's turn.

    Args:
        topic: The debate topic.
        transcript: List of dicts with 'speaker' and 'content' keys.
    """
    if transcript:
        lines = []
        for entry in transcript:
            lines.append(f"**{entry['speaker']}**: {entry['content']}")
        transcript_section = "Debate so far:\n\n" + "\n\n".join(lines)
    else:
        transcript_section = (
            "You are the first to speak. Open the debate with your position."
        )

    return SPEAKER_TURN_PROMPT.format(
        topic=topic,
        transcript_section=transcript_section,
    )


def build_consensus_prompt(topic: str, round_transcript: list[dict]) -> str:
    """Build the prompt for consensus evaluation."""
    lines = []
    for entry in round_transcript:
        lines.append(f"**{entry['speaker']}**: {entry['content']}")
    round_text = "\n\n".join(lines)

    return CONSENSUS_EXTRACTION_PROMPT.format(
        topic=topic,
        round_transcript=round_text,
    )


def build_conspectus_prompt(
    topic: str,
    participants: list[str],
    rounds: int,
    consensus_score: float,
    transcript: list[dict],
) -> str:
    """Build the prompt for generating the final conspectus."""
    lines = []
    for entry in transcript:
        lines.append(f"**{entry['speaker']}** (Round {entry.get('round', '?')}): {entry['content']}")
    transcript_text = "\n\n".join(lines)

    return CONSPECTUS_PROMPT.format(
        topic=topic,
        participants=", ".join(participants),
        rounds=rounds,
        consensus_score=consensus_score,
        transcript=transcript_text,
    )
