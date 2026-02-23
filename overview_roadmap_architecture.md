# Council of Elders - LLM Edition
## Architecture Overview, Roadmap & Resources

---

## Table of Contents

1. [Project Vision](#1-project-vision)
2. [Architecture Overview](#2-architecture-overview)
3. [Core Components](#3-core-components)
4. [Data Flow](#4-data-flow)
5. [Roadmap](#5-roadmap)
6. [Resources](#6-resources)

---

## 1. Project Vision

The **Council of Elders - LLM Edition** recreates the ancient Athenian Agora as a web application where the world's leading Large Language Models gather to debate topics posed by users. Multiple LLMs — Claude, GPT, Gemini, Grok, and others — engage in structured rounds of argumentation, responding to each other's points until a **conspectus** (shared understanding or consensus) is reached.

Users bring their own API keys (never stored on our servers) and configure the debate: choosing participants, setting the topic, and tuning parameters. The result is a living philosophical arena where AI models illuminate a topic from multiple perspectives.

### Key Principles

- **User-owned keys**: API keys are provided by users per session, transmitted over HTTPS, held only in server memory during the debate, and discarded immediately after
- **Provider-agnostic**: A unified adapter layer makes it straightforward to add new LLM providers
- **Transparency**: Every step of the debate — prompts, responses, consensus signals — is visible to the user
- **Thematic immersion**: The UI evokes the Athenian Agora — marble textures, amphitheater layouts, philosophical gravitas

---

## 2. Architecture Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│                   React (TypeScript)                          │
│                                                              │
│  ┌──────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ API Key  │  │ Topic Config │  │    Debate Viewer       │ │
│  │  Panel   │  │    Panel     │  │  (Amphitheater UI)     │ │
│  └──────────┘  └──────────────┘  └────────────────────────┘ │
│                                                              │
│         WebSocket (Socket.IO)  +  REST (HTTP)                │
└────────────────────────┬────────────────────────────────────┘
                         │  HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                               │
│                  Python (FastAPI)                             │
│                                                              │
│  ┌──────────────┐  ┌─────────────────┐  ┌────────────────┐ │
│  │   WebSocket  │  │    Debate       │  │   Consensus    │ │
│  │   Manager    │  │  Orchestrator   │  │    Engine      │ │
│  └──────────────┘  └─────────────────┘  └────────────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              LLM Provider Adapters                    │   │
│  │  ┌─────────┐ ┌────────┐ ┌────────┐ ┌──────────────┐ │   │
│  │  │Anthropic│ │ OpenAI │ │ Google │ │     xAI      │ │   │
│  │  │ (Claude)│ │ (GPT)  │ │(Gemini)│ │   (Grok)     │ │   │
│  │  └─────────┘ └────────┘ └────────┘ └──────────────┘ │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Frontend** | React 18+ with TypeScript | Rich component ecosystem, strong typing, excellent for real-time UIs |
| **Styling** | Tailwind CSS + custom theme | Rapid styling with utility classes; custom Agora theme on top |
| **State Management** | Zustand or React Context | Lightweight state management for debate state, API keys, config |
| **Build Tool** | Vite | Fast development builds, excellent HMR, simpler than Webpack |
| **Backend** | Python 3.11+ with FastAPI | Async-native, excellent for I/O-bound LLM API calls, strong typing with Pydantic |
| **WebSocket** | Socket.IO (python-socketio) | Reliable WebSocket with auto-reconnect, rooms, fallback to polling |
| **HTTP Client** | httpx (async) | Async HTTP for calling LLM APIs with streaming support |
| **Package Manager** | npm (frontend), pip/poetry (backend) | Standard tooling for each ecosystem |

### 2.3 API Key Flow

```
User enters keys in browser
        │
        ▼
Keys stored in browser sessionStorage (never localStorage)
        │
        ▼
On debate start, keys sent via HTTPS POST to backend
        │
        ▼
Backend holds keys in an in-memory session dict (keyed by session ID)
        │
        ▼
Keys used to authenticate with LLM provider APIs during debate
        │
        ▼
On debate end (or session timeout), keys are deleted from server memory
```

**Security measures:**
- Keys never written to disk, logs, or any persistent storage
- Keys transmitted only over HTTPS
- Server-side session timeout (e.g., 30 min of inactivity) auto-purges keys
- Keys are scoped to a single debate session

### 2.4 Real-Time Communication

**WebSocket (via Socket.IO)** is chosen over SSE because:
- Bidirectional: the client can send control signals (pause, stop, skip) during the debate
- Socket.IO provides automatic reconnection, room support, and fallback to HTTP long-polling
- Enables broadcasting debate events to multiple observers if needed in the future

**Events emitted from server → client:**
- `debate:turn_start` — A new speaker is about to respond
- `debate:token_stream` — Streaming tokens from the current speaker
- `debate:turn_end` — Speaker finished their response
- `debate:consensus_check` — Consensus evaluation result after a round
- `debate:concluded` — Debate has reached consensus or termination
- `debate:error` — An error occurred (API failure, rate limit, etc.)

**Events emitted from client → server:**
- `debate:start` — Begin the debate with given config
- `debate:pause` / `debate:resume` — Pause/resume the debate
- `debate:stop` — Terminate the debate early

### 2.5 Session Management

- Each debate creates an **ephemeral session** on the server, identified by a UUID
- Sessions live in an in-memory dictionary (no database for MVP)
- A session contains: API keys, debate config, conversation history, current state
- Sessions expire after 30 minutes of inactivity (configurable)
- A background task periodically cleans up expired sessions

---

## 3. Core Components

### 3.1 API Key Management Panel

**Purpose:** Allow users to enter and validate their API keys for each LLM provider before starting a debate.

**Responsibilities:**
- Present input fields for each supported provider (Anthropic, OpenAI, Google, xAI)
- Validate key format client-side (basic pattern matching)
- Validate key functionality server-side (lightweight API call, e.g., list models)
- Store keys in `sessionStorage` (cleared when tab closes)
- Show validation status (valid / invalid / untested) per provider
- Allow users to select which LLMs participate based on available keys

**Technical Details:**
- React component with controlled form inputs
- Keys are masked in the UI (password-type inputs)
- Validation endpoint: `POST /api/keys/validate` — sends key to backend, backend makes a minimal API call to verify
- No keys are logged or persisted at any point

**Interactions:**
- Feeds validated keys and selected participants to the **Topic Input & Configuration** panel
- Keys are sent to the backend when a debate starts

### 3.2 Topic Input & Debate Configuration

**Purpose:** Allow users to set the debate topic and configure debate parameters.

**Responsibilities:**
- Text input for the debate topic/question
- Selection of participating LLMs (from those with valid keys)
- Configuration of debate parameters:
  - **Max rounds**: How many rounds before forced termination (default: 10)
  - **Speakers per round**: All participants or a subset
  - **Temperature**: How creative/varied the responses should be (default: 0.7)
  - **Max tokens per response**: Cap per individual LLM turn (default: 1024)
  - **Consensus threshold**: How strongly the models must agree to conclude (default: 0.8)
  - **Persona/role assignments**: Optional — assign each LLM a perspective (e.g., "argue for", "argue against", "moderate")
- Preset topic suggestions for quick starts

**Technical Details:**
- React form component with validation
- Configuration stored in Zustand store
- Sent as JSON payload with `debate:start` WebSocket event

**Interactions:**
- Receives validated keys and available LLMs from **API Key Management Panel**
- Sends full config to the **Debate Orchestrator** (via backend) on start

### 3.3 Debate Orchestrator

**Purpose:** The core engine that runs the debate — managing turn order, constructing prompts, coordinating LLM calls, and determining when to stop.

**Responsibilities:**
- Manage the debate lifecycle: setup → rounds → consensus check → conclusion
- Determine speaker order each round (structured round-robin)
- Construct prompts for each LLM that include:
  - The original topic/question
  - The system prompt (persona, debate rules)
  - The full conversation history (what each participant has said)
  - Instructions to engage with the arguments of others
- Call the appropriate **LLM Provider Adapter** for each turn
- Stream responses back to the client via WebSocket
- After each round, invoke the **Consensus Detection Engine**
- Handle errors gracefully (skip a speaker if their API fails, notify the user)
- Enforce termination conditions (max rounds, consensus reached, user stop)

**Technical Details:**
- Python async class: `DebateOrchestrator`
- Runs as an async task per debate session
- Maintains debate state: round number, conversation history, participant list, consensus scores
- Uses structured prompts that evolve with the conversation:

```python
# Prompt structure for each turn
system_prompt = """
You are {model_name}, participating in a philosophical debate at the Agora.
Your role: {role_description}
Rules:
- Engage directly with points raised by other speakers
- Be substantive and cite reasoning
- If you agree with a point, say so explicitly
- If you disagree, explain why with evidence
- Aim for intellectual honesty over winning
"""

user_prompt = """
Topic: {topic}

Debate so far:
{conversation_history}

It is now your turn to speak. Respond to the arguments above.
"""
```

**Interactions:**
- Receives config from **Topic Input & Configuration** (via WebSocket event)
- Calls **LLM Provider Adapters** for each turn
- Invokes **Consensus Detection Engine** after each round
- Emits events to **Debate Viewer UI** via WebSocket
- On conclusion, triggers **Conspectus Generator**

### 3.4 LLM Provider Adapters

**Purpose:** Provide a unified interface for calling different LLM APIs, abstracting away provider-specific details.

**Responsibilities:**
- Uniform `generate(messages, config)` interface across all providers
- Handle streaming responses from each provider
- Map between our internal message format and each provider's format
- Handle rate limiting with exponential backoff
- Report token usage per call
- Graceful error handling and timeout management

**Supported Providers (MVP):**

| Provider | Models | SDK/API |
|----------|--------|---------|
| **Anthropic** | Claude Opus, Claude Sonnet | `anthropic` Python SDK |
| **OpenAI** | GPT-4o, GPT-4, o1/o3 | `openai` Python SDK |
| **Google** | Gemini Pro, Gemini Ultra | `google-genai` Python SDK |
| **xAI** | Grok | `openai` Python SDK (xAI uses OpenAI-compatible API) |

**Technical Details:**
- Abstract base class `LLMAdapter` with concrete implementations per provider
- Each adapter handles the provider-specific message format translation:

```python
class LLMAdapter(ABC):
    @abstractmethod
    async def generate_stream(
        self,
        messages: list[Message],
        config: GenerationConfig,
        api_key: str,
    ) -> AsyncGenerator[str, None]:
        """Yield tokens as they are generated."""
        ...

    @abstractmethod
    async def validate_key(self, api_key: str) -> bool:
        """Check if the API key is valid."""
        ...

class AnthropicAdapter(LLMAdapter):
    ...

class OpenAIAdapter(LLMAdapter):
    ...

class GeminiAdapter(LLMAdapter):
    ...

class XAIAdapter(LLMAdapter):
    # Uses OpenAI SDK with custom base URL
    ...
```

- Streaming is handled via async generators
- Rate limit errors trigger exponential backoff with jitter
- Token usage tracked per response for cost estimation

**Interactions:**
- Called by the **Debate Orchestrator** during each turn
- Called by the **API Key Management Panel** backend endpoint for key validation
- Called by the **Conspectus Generator** for final summary generation

### 3.5 Consensus Detection Engine

**Purpose:** Determine whether the participating LLMs have reached a sufficient level of agreement on the topic to conclude the debate.

**Responsibilities:**
- Analyze the latest round of responses for signals of agreement or disagreement
- Produce a consensus score (0.0 = total disagreement, 1.0 = full consensus)
- Detect stagnation (same arguments repeated without progress)
- Report which points are agreed upon and which remain contested

**Approach — Multi-Signal Consensus Detection:**

The engine uses three complementary methods:

#### Signal 1: Explicit Agreement Markers
Parse each response for phrases indicating agreement or disagreement:
- Agreement: "I agree with...", "Building on X's point...", "That's correct...", "We seem to converge on..."
- Disagreement: "I disagree...", "However, I must counter...", "That misses the point..."
- Weight these markers by position (conclusions weighted higher than caveats)

#### Signal 2: Position Extraction & Comparison
- After each round, ask a lightweight LLM call (or use the fastest available model) to extract the core positions of each participant as structured data
- Compare positions across participants using a similarity metric
- Track how positions evolve across rounds (convergence vs divergence)

```python
# Position extraction prompt
"""
Based on {speaker}'s latest response, extract their core position as a list of claims:
1. ...
2. ...
3. ...

For each claim, rate their confidence: strong / moderate / tentative
"""
```

#### Signal 3: Stagnation Detection
- If the extracted positions haven't changed significantly for 2+ rounds, flag stagnation
- If token-level similarity between consecutive responses exceeds a threshold, flag repetition

**Consensus Score Calculation:**
```
consensus_score = (
    w1 * agreement_marker_score +
    w2 * position_similarity_score +
    w3 * (1 - stagnation_penalty)
)
```
Where `w1 + w2 + w3 = 1.0` (configurable weights, defaults: 0.3, 0.5, 0.2)

**Termination Conditions (any one triggers conclusion):**
1. `consensus_score >= consensus_threshold` (configurable, default 0.8)
2. `current_round >= max_rounds`
3. Stagnation detected for 3+ consecutive rounds
4. User manually stops the debate

**Interactions:**
- Called by the **Debate Orchestrator** after each round
- Returns consensus score and analysis to the Orchestrator
- Results are emitted to the **Debate Viewer UI**

### 3.6 Debate Viewer UI

**Purpose:** Display the ongoing debate in real time with an engaging, thematically immersive interface.

**Responsibilities:**
- Show each speaker's responses as they stream in (token by token)
- Identify speakers with distinct avatars, colors, and names
- Display round progression and debate status
- Show consensus meter/indicator updating after each round
- Allow user controls: pause, resume, stop, scroll through history
- Show token usage / estimated cost per speaker
- Display the final conspectus when the debate concludes

**UI Layout — Amphitheater Design:**

```
┌──────────────────────────────────────────────────┐
│                  THE AGORA                         │
│              ┌──────────────┐                      │
│              │  DEBATE TOPIC │                      │
│              └──────────────┘                      │
│                                                    │
│     ┌─────┐                        ┌─────┐        │
│     │CLAUDE│                        │ GPT │        │
│     │  🏛️  │                        │  🏛️  │        │
│     └─────┘                        └─────┘        │
│                                                    │
│              ┌─────┐    ┌─────┐                    │
│              │GEMINI│    │GROK │                    │
│              │  🏛️   │    │  🏛️  │                    │
│              └─────┘    └─────┘                    │
│                                                    │
│  ┌──────────────────────────────────────────────┐ │
│  │           DEBATE TRANSCRIPT                   │ │
│  │                                               │ │
│  │  [Claude - Round 1]                           │ │
│  │  The fundamental question of...               │ │
│  │                                               │ │
│  │  [GPT-4 - Round 1]                            │ │
│  │  While I appreciate Claude's framing...       │ │
│  │                                               │ │
│  └──────────────────────────────────────────────┘ │
│                                                    │
│  ┌──────────────────────┐   ┌──────────────────┐  │
│  │ Consensus: ████░░ 65%│   │ Round: 3 / 10    │  │
│  └──────────────────────┘   │ ⏸ Pause │ ⏹ Stop │  │
│                              └──────────────────┘  │
└──────────────────────────────────────────────────┘
```

**Technical Details:**
- React components with Tailwind styling + custom Agora theme
- Socket.IO client for real-time updates
- Smooth auto-scroll with scroll-lock toggle
- Markdown rendering for LLM responses (react-markdown)
- Animated consensus meter
- Speaker indicators with distinct colors and icons per provider

**Interactions:**
- Receives all debate events from the backend via WebSocket
- Sends control events (pause, stop) back to the **Debate Orchestrator**
- Displays consensus data from the **Consensus Detection Engine**
- Shows the final output from the **Conspectus Generator**

### 3.7 Conspectus Generator

**Purpose:** When the debate concludes, synthesize a final summary of what was debated, where the LLMs agreed and disagreed, and what the consensus position is.

**Responsibilities:**
- Take the full debate transcript and consensus analysis as input
- Generate a structured summary:
  - **Topic**: The original question
  - **Participants**: Who debated
  - **Key arguments**: Major points raised by each side
  - **Points of agreement**: Where all/most participants converged
  - **Points of disagreement**: Where positions remain divergent
  - **Consensus position**: The synthesized shared understanding
  - **Debate statistics**: Rounds, tokens used, estimated cost

**Technical Details:**
- Uses one of the participating LLMs (user-configurable, or the fastest available) to generate the summary
- Prompt includes the full transcript + consensus engine analysis
- Output is structured markdown

```python
conspectus_prompt = """
You are a neutral scribe at the Athenian Agora. The debate on the following
topic has concluded. Produce a conspectus — a comprehensive summary.

Topic: {topic}
Participants: {participants}
Number of rounds: {rounds}
Final consensus score: {score}

Full transcript:
{transcript}

Consensus analysis:
{consensus_analysis}

Write a structured conspectus with these sections:
1. Overview — What was debated and why
2. Key Arguments — The strongest arguments from each participant
3. Points of Agreement — Where the speakers converged
4. Remaining Disagreements — Where they could not agree
5. Synthesis — The final conspectus: what can we conclude?
"""
```

**Interactions:**
- Triggered by the **Debate Orchestrator** when the debate concludes
- Uses **LLM Provider Adapters** to generate the summary
- Output is sent to the **Debate Viewer UI** for display and optional export

---

## 4. Data Flow

### 4.1 Complete Debate Lifecycle

```
1. USER SETUP
   User opens app → Enters API keys → Keys validated → Keys stored in sessionStorage

2. DEBATE CONFIGURATION
   User enters topic → Selects participants → Configures parameters → Clicks "Begin Debate"

3. SESSION CREATION
   Frontend sends config + keys via HTTPS → Backend creates session → WebSocket connection established

4. DEBATE EXECUTION (per round)
   For each participant in round:
     a. Orchestrator constructs prompt (topic + history + persona)
     b. Orchestrator calls LLM Adapter with prompt + API key
     c. Adapter streams response tokens
     d. Tokens relayed to frontend via WebSocket
     e. Full response added to conversation history

5. CONSENSUS CHECK (after each round)
   Orchestrator sends round data to Consensus Engine →
   Engine analyzes agreement signals → Returns score →
   Score emitted to frontend → If threshold met, proceed to step 6

6. DEBATE CONCLUSION
   Orchestrator triggers Conspectus Generator →
   Generator summarizes transcript → Summary sent to frontend →
   Session keys purged from server memory

7. CLEANUP
   User can export transcript/conspectus →
   Session expires after timeout →
   All in-memory data garbage collected
```

### 4.2 Error Handling Strategy

| Error | Handling |
|-------|----------|
| **API key invalid** | Caught during validation; user prompted to re-enter |
| **Rate limit hit** | Exponential backoff (1s, 2s, 4s, 8s); notify user of delay |
| **API timeout** | Retry once; if still failing, skip speaker for this round with notice |
| **Provider outage** | Skip speaker, continue with remaining participants, notify user |
| **WebSocket disconnect** | Socket.IO auto-reconnect; debate state preserved server-side |
| **All providers fail** | Pause debate, notify user, allow retry or termination |
| **Session timeout** | Purge keys, notify user to restart if they return |

---

## 5. Roadmap

### Phase 1: Foundation & MVP

**Goal:** A working prototype where 2 LLMs debate a topic in structured rounds with a basic UI.

| Task | Details |
|------|---------|
| Project scaffolding | Set up React (Vite) frontend + FastAPI backend, monorepo structure |
| LLM Adapter: Anthropic | Implement Claude adapter with streaming |
| LLM Adapter: OpenAI | Implement GPT adapter with streaming |
| API Key Panel (basic) | Simple form for entering Anthropic and OpenAI keys |
| Topic Input (basic) | Text input for topic, basic config (max rounds) |
| Debate Orchestrator (basic) | Round-robin turn management, prompt construction, history tracking |
| WebSocket Integration | Socket.IO setup, event emission for debate turns |
| Debate Viewer (basic) | Simple transcript view with speaker labels, streaming text |
| Manual termination | User can stop the debate, see full transcript |

**Deliverable:** Two LLMs can debate a topic with streaming responses displayed in real time.

### Phase 2: Multi-LLM & Consensus

**Goal:** Support all 4 providers, add consensus detection, and produce a conspectus.

| Task | Details |
|------|---------|
| LLM Adapter: Gemini | Implement Google Gemini adapter |
| LLM Adapter: xAI | Implement Grok adapter (OpenAI-compatible) |
| Key validation | Server-side key validation for all providers |
| Full participant selection | UI for choosing which LLMs participate |
| Consensus Detection Engine | Implement multi-signal consensus scoring |
| Conspectus Generator | Post-debate summary generation |
| Debate parameters | Full config UI (temperature, max tokens, threshold, personas) |
| Token usage tracking | Count tokens per speaker, estimate costs |
| Error handling | Graceful recovery from API failures, rate limits |

**Deliverable:** Full multi-LLM debates with automatic consensus detection and summary generation.

### Phase 3: Agora Theme & UX Polish

**Goal:** Transform the UI into an immersive Agora experience with polished UX.

| Task | Details |
|------|---------|
| Agora theme design | Marble textures, amphitheater layout, Greek typography accents |
| Speaker avatars & identity | Distinct visual identity per LLM (icon, color, speaking style) |
| Animated consensus meter | Visual progress indicator with animations |
| Debate timeline | Navigable timeline showing rounds and key moments |
| Responsive design | Mobile-friendly layout |
| Debate export | Download transcript and conspectus as Markdown/PDF |
| Preset topics | Curated philosophical and contemporary debate topics |
| Toast notifications | User-friendly notifications for errors, state changes |
| Loading states & animations | Smooth transitions, speaking indicators, typing effects |

**Deliverable:** A visually polished, thematically immersive web application.

### Phase 4: Advanced Features

**Goal:** Enhanced debate modes, social features, and production readiness.

| Task | Details |
|------|---------|
| Debate modes | Socratic dialogue, Oxford-style, free-form, moderated |
| Audience/user participation | Let the user interject as a debate participant |
| Debate history (local) | Save past debates in browser localStorage |
| Shareable debates | Generate shareable links to debate transcripts |
| Cost calculator | Pre-debate cost estimation based on config |
| Additional LLM providers | Mistral, Cohere, Meta Llama (via API), DeepSeek etc. |
| Accessibility (a11y) | Screen reader support, keyboard navigation, high contrast |
| Deployment & CI/CD | Docker, cloud deployment (Vercel/Railway/Fly.io), automated tests |
| Rate limit management | Smart scheduling across providers, parallel calls where possible |

**Deliverable:** A feature-rich, production-ready application.

---

## 6. Resources

### 6.1 LLM Provider APIs

| Provider | API Documentation | Python SDK | Notes |
|----------|------------------|------------|-------|
| **Anthropic (Claude)** | [docs.anthropic.com](https://docs.anthropic.com/) | `anthropic` | Messages API with streaming |
| **OpenAI (GPT)** | [platform.openai.com/docs](https://platform.openai.com/docs/) | `openai` | Chat Completions API with streaming |
| **Google (Gemini)** | [ai.google.dev/docs](https://ai.google.dev/docs) | `google-genai` | Gemini API with streaming |
| **xAI (Grok)** | [docs.x.ai](https://docs.x.ai/) | `openai` (compatible) | Uses OpenAI-compatible API with custom base URL |

### 6.2 Key Libraries & Packages

**Backend (Python):**

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework with async support |
| `uvicorn` | ASGI server for FastAPI |
| `python-socketio` | WebSocket support (Socket.IO server) |
| `anthropic` | Anthropic/Claude API SDK |
| `openai` | OpenAI API SDK (also used for xAI) |
| `google-genai` | Google Gemini API SDK |
| `httpx` | Async HTTP client |
| `pydantic` | Data validation and settings management |
| `python-dotenv` | Environment variable management (dev only) |

**Frontend (JavaScript/TypeScript):**

| Package | Purpose |
|---------|---------|
| `react` / `react-dom` | UI framework |
| `typescript` | Type safety |
| `vite` | Build tool and dev server |
| `tailwindcss` | Utility-first CSS |
| `socket.io-client` | WebSocket client (Socket.IO) |
| `zustand` | Lightweight state management |
| `react-markdown` | Markdown rendering for LLM responses |
| `react-syntax-highlighter` | Code block highlighting in responses |
| `framer-motion` | Animations (consensus meter, transitions) |
| `lucide-react` | Icon library |

### 6.3 Development Tools

| Tool | Purpose |
|------|---------|
| `ruff` | Python linter and formatter |
| `mypy` | Python type checking |
| `pytest` | Python testing |
| `eslint` | JavaScript/TypeScript linting |
| `prettier` | Code formatting |
| `vitest` | Frontend unit testing |

### 6.4 Infrastructure

| Component | Recommendation | Notes |
|-----------|---------------|-------|
| **Frontend Hosting** | Vercel or Netlify | Free tier available, excellent for React SPAs |
| **Backend Hosting** | Railway, Fly.io, or Render | Support for WebSockets, Python, affordable |
| **Domain** | Custom domain (optional) | Can use platform subdomains for MVP |
| **SSL/TLS** | Platform-provided | All platforms above provide free HTTPS |
| **Database** | None (MVP) | In-memory sessions only; add Redis later if needed |
| **Monitoring** | Sentry (free tier) | Error tracking for production |

### 6.5 Project Structure

```
Council-of-Elders---LLM-Edition/
├── frontend/                      # React application
│   ├── src/
│   │   ├── components/
│   │   │   ├── ApiKeyPanel/       # API key input and validation
│   │   │   ├── DebateConfig/      # Topic and parameter configuration
│   │   │   ├── DebateViewer/      # Main debate display
│   │   │   ├── ConsensusMeter/    # Consensus visualization
│   │   │   ├── Conspectus/        # Final summary display
│   │   │   └── common/            # Shared UI components
│   │   ├── hooks/                 # Custom React hooks
│   │   ├── stores/                # Zustand state stores
│   │   ├── services/              # API and WebSocket client services
│   │   ├── types/                 # TypeScript type definitions
│   │   ├── styles/                # Global styles and Agora theme
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/                    # Static assets (icons, textures)
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── vite.config.ts
│
├── backend/                       # FastAPI application
│   ├── app/
│   │   ├── main.py               # FastAPI app + Socket.IO mount
│   │   ├── config.py             # App configuration
│   │   ├── models/               # Pydantic models
│   │   │   ├── debate.py         # Debate, Round, Message models
│   │   │   └── providers.py      # Provider config models
│   │   ├── adapters/             # LLM provider adapters
│   │   │   ├── base.py           # Abstract base adapter
│   │   │   ├── anthropic.py      # Claude adapter
│   │   │   ├── openai_adapter.py # GPT adapter
│   │   │   ├── gemini.py         # Gemini adapter
│   │   │   └── xai.py            # Grok adapter
│   │   ├── orchestrator/         # Debate orchestration
│   │   │   ├── engine.py         # Main debate orchestrator
│   │   │   ├── prompts.py        # Prompt templates
│   │   │   └── consensus.py      # Consensus detection engine
│   │   ├── services/             # Business logic
│   │   │   ├── session.py        # Session management
│   │   │   ├── conspectus.py     # Summary generation
│   │   │   └── cost.py           # Token/cost tracking
│   │   ├── api/                  # REST API routes
│   │   │   └── keys.py           # Key validation endpoints
│   │   └── ws/                   # WebSocket event handlers
│   │       └── debate.py         # Debate WebSocket events
│   ├── tests/                    # Backend tests
│   ├── requirements.txt
│   └── pyproject.toml
│
├── overview_roadmap_architecture.md   # This document
├── TODO.md                            # Project task tracker
└── README.md                          # Project README
```
