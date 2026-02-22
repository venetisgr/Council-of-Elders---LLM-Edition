# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Council of Elders - LLM Edition is a web application that recreates the ancient Athenian Agora as a multi-LLM debate platform. Users provide their own API keys, select LLM participants (Claude, GPT, Gemini, Grok), pose a topic, and watch the models debate in structured rounds until consensus is reached. A final conspectus summarizes the outcome.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18+, TypeScript, Vite, Tailwind CSS, Zustand, Socket.IO client |
| Backend | Python 3.11+, FastAPI, python-socketio, httpx (async), Pydantic |
| Real-time | WebSocket via Socket.IO (bidirectional: streaming tokens + user controls) |
| LLM SDKs | `anthropic`, `openai` (also for xAI/Grok), `google-genai` |

## Project Structure

Monorepo with two top-level directories:

- `frontend/` — React SPA (Vite build, `src/components/`, `src/stores/`, `src/services/`)
- `backend/` — FastAPI app (`app/adapters/`, `app/orchestrator/`, `app/api/`, `app/ws/`, `app/models/`)

See `overview_roadmap_architecture.md` §6.5 for the full directory tree.

## Development Commands

### Frontend (`frontend/`)
```bash
npm install              # Install dependencies
npm run dev              # Start dev server (Vite)
npm run build            # Production build
npm run lint             # ESLint
npx vitest               # Run tests
npx vitest run <file>    # Run a single test file
```

### Backend (`backend/`)
```bash
pip install -r requirements.txt    # Install dependencies
uvicorn app.main:app --reload      # Start dev server
pytest                             # Run all tests
pytest tests/test_foo.py -k name   # Run a single test by name
ruff check .                       # Lint
ruff format .                      # Format
```

## Architecture Essentials

### Core Components
1. **API Key Management Panel** — Frontend form; keys stored in browser `sessionStorage`, sent to backend per-request
2. **Topic Input & Configuration** — Debate topic, participant selection, parameters (max rounds, temperature, consensus threshold)
3. **Debate Orchestrator** (`backend/app/orchestrator/engine.py`) — Manages round-robin turns, constructs prompts with full conversation history, invokes consensus checks, enforces termination
4. **LLM Provider Adapters** (`backend/app/adapters/`) — Abstract `LLMAdapter` base class with `generate_stream()` and `validate_key()`. One concrete class per provider.
5. **Consensus Detection Engine** (`backend/app/orchestrator/consensus.py`) — Three signals: explicit agreement markers, position extraction/comparison, stagnation detection. Produces a 0.0–1.0 consensus score.
6. **Debate Viewer UI** — Amphitheater-themed real-time transcript with streaming tokens, consensus meter, round counter
7. **Conspectus Generator** (`backend/app/services/conspectus.py`) — Uses an LLM to produce a structured summary when the debate concludes

### WebSocket Event Protocol
Server → Client: `debate:turn_start`, `debate:token_stream`, `debate:turn_end`, `debate:consensus_check`, `debate:concluded`, `debate:error`
Client → Server: `debate:start`, `debate:pause`, `debate:resume`, `debate:stop`

### Data Flow
User enters keys & config → Frontend sends via HTTPS → Backend creates in-memory session → Orchestrator runs rounds (adapter calls → streaming tokens via WS) → Consensus check after each round → On conclusion, conspectus generated → Keys purged from server memory

## Security: API Key Handling

API keys are ephemeral throughout the entire flow:
- **Browser**: stored in `sessionStorage` (not `localStorage`), cleared when the tab closes
- **Transport**: sent only over HTTPS
- **Server**: held in an in-memory session dict, never written to disk, logs, or any persistent store
- **Cleanup**: purged when the debate ends or the session times out (30 min inactivity)

## Adding a New LLM Provider

1. Create `backend/app/adapters/<provider>.py`
2. Subclass `LLMAdapter` from `backend/app/adapters/base.py`
3. Implement `async generate_stream(messages, config, api_key) -> AsyncGenerator[str, None]`
4. Implement `async validate_key(api_key) -> bool`
5. Register the adapter in the provider factory
6. Add the provider to the frontend's API Key Panel and participant selector

Note: xAI/Grok uses the OpenAI-compatible API, so it reuses the `openai` SDK with a custom `base_url`.

## Key References

- `overview_roadmap_architecture.md` — Full architecture, component designs, data flow diagrams, phased roadmap, and resource list
- `TODO.md` — Phase-by-phase implementation checklist with current progress
