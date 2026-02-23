# Ancient Athenian Agora — LLM Edition

**Live at [agora-llm.vercel.app](https://agora-llm.vercel.app/)**

A first-of-its-kind platform that brings the world's leading AI models together for structured, multi-round deliberation on any topic you choose. Instead of asking one model and hoping for the best, pit Claude, GPT, Gemini, Grok, DeepSeek, Kimi, Qwen, and GLM against each other in a live debate — and let them argue, challenge, and refine each other's reasoning in real time.

Think of it as a **virtual panel of AI experts**. Each participant brings a different training background, knowledge base, and reasoning style. By forcing them to engage directly with each other's arguments — agreeing where they find common ground and pushing back where they don't — the Agora surfaces insights, blind spots, and nuances that no single model would produce alone.

## Use It To

- **Stress-test an idea** — Get diverse AI perspectives before committing to a strategy, architecture, or decision.
- **Research complex topics** — Let multiple models debate the evidence and trade-offs so you see the full picture.
- **Evaluate AI reasoning** — Compare how different models approach the same problem, where they agree, and where they diverge.
- **Generate robust conclusions** — The consensus engine and final conspectus distill hours of potential research into a structured, multi-perspective summary.
- **Learn and explore** — Pose philosophical, scientific, or creative questions and watch genuinely different viewpoints collide.

## Supported LLM Providers

| Provider | Models | Notes |
|----------|--------|-------|
| **Anthropic** (Claude) | claude-opus-4-6, claude-sonnet-4-6, claude-haiku-4-5 | Native SDK |
| **OpenAI** | gpt-5.2, gpt-4o, gpt-4o-mini | Native SDK |
| **Google** (Gemini) | gemini-3-pro-preview, gemini-2.5-pro-preview, gemini-2.0-flash, gemini-2.0-flash-lite | Native SDK |
| **xAI** (Grok) | grok-3, grok-3-mini, grok-2, grok-2-mini | OpenAI-compatible |
| **DeepSeek** | deepseek-chat, deepseek-reasoner | OpenAI-compatible |
| **Kimi** (Moonshot) | moonshot-v1-128k, moonshot-v1-32k, moonshot-v1-8k | OpenAI-compatible |
| **Qwen** (Alibaba) | qwen3-max, qwen3.5-plus, qwen-plus | OpenAI-compatible |
| **GLM** (Zhipu) | glm-5, glm-4-plus | OpenAI-compatible |

You bring your own API keys. Keys are stored only in your browser's `sessionStorage` (cleared when the tab closes), transmitted over HTTPS, held in server memory only during the debate, and purged when the debate ends or the session times out (30 minutes).

---

## How the Agora Works

### Debate Flow

A debate proceeds in **rounds**. In each round every participant speaks exactly once in the order they were added (round-robin). Each participant receives the full transcript of everything said so far, plus a system prompt that establishes their identity, persona (if assigned), and the rules of the Agora. They are instructed to engage directly with other speakers' arguments, agree explicitly when they find common ground, and disagree with precision when they don't.

After all participants have spoken in a round, a **consensus check** is performed. If the composite consensus score meets or exceeds the configured threshold, the debate ends. Otherwise the next round begins. The debate also terminates when the maximum number of rounds is reached or when stagnation is detected for three consecutive rounds.

### Consensus Score (0.0 – 1.0)

The consensus score is a **weighted composite** of three independent signals, computed after every round:

#### Signal 1 — Agreement Markers (weight: 25%)

A text-scanning heuristic that counts how often participants use explicit agreement phrases versus disagreement phrases in their responses.

**Agreement phrases:** "i agree", "i concur", "that's correct", "building on", "exactly right", "well said", "i share", "common ground", "we seem to converge", "as [name] correctly pointed out", "aligns with my view", "i must acknowledge"

**Disagreement phrases:** "i disagree", "i must counter", "however", "on the contrary", "that misses", "i take issue", "fundamentally flawed", "i challenge", "that overlooks", "insufficient"

Formula: `agreement_count / (agreement_count + disagreement_count)`. If no markers are found, the score defaults to 0.5 (neutral).

#### Signal 2 — LLM Moderator Analysis (weight: 60%)

The participant you select as **Moderator** in the Argument Parameters also acts as an impartial judge. After each round, the moderator LLM receives the round's transcript and is prompted as an "impartial observer at the Agora" to return a structured JSON assessment containing:

- **consensus_score** — a 0.0 to 1.0 rating of how much the speakers agree
- **agreed_points** — specific points where speakers converge
- **contested_points** — specific points where they diverge
- **stagnation** — whether arguments are repetitive and not advancing
- **summary** — a one-sentence assessment of the debate's current state

This call uses a low temperature (0.1) and a 512-token limit for deterministic, concise analysis. If the call fails for any reason, the LLM score defaults to 0.5.

#### Signal 3 — Stagnation Detection (weight: 15%)

Detects whether the debate is going in circles by comparing the vocabulary of the current round to the previous round. All responses in each round are lowercased and split into word sets, then the overlap ratio is computed:

Formula: `|current_words ∩ previous_words| / |current_words ∪ previous_words|`

If more than **80%** of the words overlap between rounds, stagnation is flagged. When stagnation is detected, a penalty of 0.3 is applied (the signal contributes 0.105 instead of 0.15). Stagnation cannot be detected in the first round since there is no prior round to compare against.

#### Final Composite Formula

```
consensus = 0.25 × marker_score + 0.60 × llm_score + 0.15 × (1.0 − stagnation_penalty)
```

The result is clamped to [0.0, 1.0]. When there is no stagnation the third term contributes a full 0.15; when stagnation is detected the penalty (0.3) reduces it to 0.105, lowering the composite by 0.045.

### Consensus Threshold

The threshold (default 80%, configurable from 0% to 100%) is the target composite score that ends the debate. After every round, if `consensus_score ≥ threshold`, the debate concludes with "consensus reached". A lower threshold means the debate ends sooner (participants don't need to agree as strongly); a higher threshold demands near-total alignment before the debate will stop on its own.

Even if the threshold is never reached, the debate still terminates when:

- The maximum number of rounds is exhausted.
- Stagnation is detected for **3 consecutive rounds**, indicating the participants are repeating themselves and further rounds are unlikely to produce new insight.

### Conspectus (Final Summary)

When the debate concludes — whether by consensus, stagnation, max rounds, or manual stop — the moderator LLM generates a **conspectus**: a structured summary of the entire deliberation. It receives the full transcript, participant names, round count, and final consensus score, and produces five sections: Overview, Key Arguments, Points of Agreement, Remaining Disagreements, and Synthesis.

### Configuration Reference

| Setting | Default | Description |
|---------|---------|-------------|
| Temperature | 0.45 | Per-participant. Controls randomness (0.0–2.0). Higher = more creative, lower = more focused. |
| Persona | None | Per-participant. An optional perspective (e.g. "pragmatist", "skeptic") injected into the system prompt. |
| Max Rounds | 10 | Upper limit on debate rounds (1–50). |
| Max Tokens / Turn | 1024 | Maximum tokens each participant can produce per turn (100–4096). |
| Consensus Threshold | 80% | The composite consensus score required to end the debate (0%–100%). |
| Moderator | First participant | The participant whose LLM evaluates consensus after each round and writes the final conspectus. |

---

## Running Locally

### Prerequisites

- **Node.js** 18+ and **npm**
- **Python** 3.11+
- API keys for at least one supported provider

### 1. Clone the Repository

```bash
git clone https://github.com/venetisgr/Council-of-Elders---LLM-Edition.git
cd Council-of-Elders---LLM-Edition
```

### 2. Start the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend starts on `http://localhost:8000`.

### 3. Start the Frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend starts on `http://localhost:5173`. Vite's dev proxy automatically forwards `/api` and `/socket.io` requests to the backend on port 8000, so no environment variables are needed for local development.

### 4. Open the App

Navigate to `http://localhost:5173` in your browser. Enter your API keys, add at least 2 participants, type a topic, and start a debate.

### Running Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npx vitest
```

### Linting

```bash
# Backend
cd backend
ruff check .
ruff format .

# Frontend
cd frontend
npm run lint
```

---

## Deploying to Vercel

The repository includes a `vercel.json` configuration that deploys the frontend as a static Vite build and routes API requests to a lightweight serverless function at `api/index.py`.

### 1. Import the Repository

1. Go to [vercel.com](https://vercel.com) and sign in.
2. Click **Add New Project** and import `venetisgr/Council-of-Elders---LLM-Edition` from GitHub.
3. Vercel will auto-detect the Vite framework from `vercel.json`.

### 2. Configure Environment Variables (if needed)

In the Vercel project settings, add:

| Variable | Value | Purpose |
|----------|-------|---------|
| `CORS_ORIGINS` | Your Vercel deployment URL (e.g. `https://your-app.vercel.app`) | Allows the backend API to accept requests from the frontend |

### 3. Deploy

Click **Deploy**. Vercel will:

- Run `cd frontend && npm install && npm run build` (from `vercel.json`)
- Serve the built static files from `frontend/dist/`
- Route `/api/*` and `/health` requests to the serverless function in `api/index.py`

### Important Notes on Vercel Deployment

The Vercel serverless function (`api/index.py`) is a **stateless, lightweight** version of the backend that supports:

- API key validation
- Provider listing
- Stateless debate turn, consensus, and conspectus endpoints

**WebSocket / real-time streaming is not available on Vercel** because serverless functions cannot maintain persistent connections. On Vercel the debate runs via stateless HTTP requests rather than Socket.IO streaming.

For the full real-time streaming experience with Socket.IO, deploy the backend separately on a platform that supports persistent connections (e.g. Railway, Fly.io, Render, or a VPS) and set the `VITE_BACKEND_URL` environment variable in the frontend to point to it:

```bash
# frontend/.env
VITE_BACKEND_URL=https://your-backend.railway.app
```

Then set `CORS_ORIGINS` on the backend to allow requests from your Vercel frontend URL:

```bash
# backend/.env
CORS_ORIGINS=https://your-app.vercel.app
```

---

## Project Structure

```
.
├── vercel.json                    # Vercel deployment config
├── api/
│   ├── index.py                   # Vercel serverless entry point
│   └── requirements.txt           # Serverless dependencies
│
├── frontend/
│   ├── package.json               # React/Vite/Tailwind dependencies
│   ├── vite.config.ts             # Dev server + proxy config
│   ├── index.html                 # Vite entry point
│   ├── .env.example               # VITE_BACKEND_URL
│   └── src/
│       ├── components/            # React components
│       │   ├── DebateConfig/      # API keys, participant selector, parameters
│       │   ├── DebateViewer/      # Real-time debate transcript + consensus meter
│       │   └── HowItWorks.tsx     # Detailed explanation panel
│       ├── stores/                # Zustand state management
│       ├── services/              # API client + Socket.IO client
│       └── types/                 # TypeScript interfaces + provider definitions
│
├── backend/
│   ├── requirements.txt           # FastAPI + LLM SDK dependencies
│   ├── .env.example               # CORS_ORIGINS
│   └── app/
│       ├── main.py                # FastAPI entry point + Socket.IO mount
│       ├── config.py              # App configuration
│       ├── adapters/              # LLM provider adapters
│       │   ├── base.py            # Abstract LLMAdapter
│       │   ├── anthropic_adapter.py
│       │   ├── openai_adapter.py  # Base for OpenAI-compatible providers
│       │   ├── gemini_adapter.py
│       │   ├── xai_adapter.py
│       │   ├── deepseek_adapter.py
│       │   ├── kimi_adapter.py
│       │   ├── qwen_adapter.py
│       │   ├── glm_adapter.py
│       │   └── factory.py         # Provider → adapter registry
│       ├── api/                   # REST endpoints
│       ├── orchestrator/          # Debate engine + consensus detection
│       ├── services/              # Session manager + conspectus generator
│       ├── ws/                    # Socket.IO event handlers
│       └── models/                # Pydantic data models
│
└── docs/
    └── overview_roadmap_architecture.md
```

---

## Security: API Key Handling

API keys are ephemeral throughout the entire flow:

- **Browser**: stored in `sessionStorage` (not `localStorage`), cleared when the tab closes
- **Transport**: sent only over HTTPS
- **Server**: held in an in-memory session dict, never written to disk, logs, or any persistent store
- **Cleanup**: purged when the debate ends or the session times out (30 min inactivity)

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, Zustand, Socket.IO client |
| Backend | Python 3.11+, FastAPI, python-socketio, httpx (async), Pydantic |
| Real-time | WebSocket via Socket.IO (bidirectional: streaming tokens + user controls) |
| LLM SDKs | `anthropic`, `openai` (also for xAI, DeepSeek, Kimi, Qwen, GLM), `google-genai` |

### Frontend

| Category | Technology | Purpose |
|----------|-----------|---------|
| Core | **React 18** | UI framework for building interactive components |
| Core | **TypeScript** | Static typing and type safety |
| Core | **Vite** | Build tool and dev server with HMR |
| Styling | **Tailwind CSS** | Utility-first CSS framework |
| Styling | **PostCSS** + **Autoprefixer** | CSS processing and vendor prefixing |
| State | **Zustand** | Lightweight state management |
| Real-time | **Socket.IO Client** | WebSocket communication for streaming tokens |
| Animation | **Framer Motion** | Smooth UI transitions and animations |
| Rendering | **react-markdown** + **remark-gfm** + **rehype-raw** | Markdown rendering with GitHub Flavored Markdown |
| Rendering | **react-syntax-highlighter** | Syntax highlighting for code blocks |
| Icons | **Lucide React** | SVG icon library |
| Linting | **ESLint** + **typescript-eslint** | Code quality and style enforcement |

### Backend

| Category | Technology | Purpose |
|----------|-----------|---------|
| Framework | **FastAPI** | Async Python web framework for REST APIs |
| Server | **Uvicorn** | ASGI server with WebSocket support |
| Real-time | **python-socketio** | Server-side WebSocket event handling |
| HTTP | **httpx** | Async HTTP client for LLM API calls |
| Validation | **Pydantic** | Data validation and serialization via type hints |
| Config | **python-dotenv** | Environment variable management |
| LLM SDK | **anthropic** | Anthropic Claude API client |
| LLM SDK | **openai** | OpenAI API client (also powers xAI, DeepSeek, Kimi, Qwen, GLM) |
| LLM SDK | **google-genai** | Google Gemini API client |
| Testing | **pytest** + **pytest-asyncio** | Unit and async integration testing |

---

## Contributing

Found a bug or have a suggestion? [Open an issue](https://github.com/venetisgr/Council-of-Elders---LLM-Edition/issues).

If you enjoy the Agora, consider [starring the repository](https://github.com/venetisgr/Council-of-Elders---LLM-Edition) — it helps others discover the project.


