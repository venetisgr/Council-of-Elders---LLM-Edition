# Council of Elders - LLM Edition: TODO

> Task tracker for the project. Phases map to the roadmap in `overview_roadmap_architecture.md`.

---

## Legend

- [ ] Not started
- [~] In progress
- [x] Completed

---

## Phase 0: Planning & Setup

- [x] Create project architecture overview (`overview_roadmap_architecture.md`)
- [x] Create task tracker (`TODO.md`)
- [x] Initialize monorepo structure (`frontend/` + `backend/`)
- [x] Set up React project with Vite + TypeScript + Tailwind CSS
- [x] Set up FastAPI project with project structure
- [x] Configure linting and formatting (ESLint, Ruff)
- [x] Set up Socket.IO on both frontend and backend
- [ ] Create basic dev environment documentation in README

---

## Phase 1: Foundation & MVP

### Backend — LLM Adapters
- [x] Define abstract `LLMAdapter` base class
- [x] Implement Anthropic (Claude) adapter with streaming
- [x] Implement OpenAI (GPT) adapter with streaming
- [x] Write unit tests for both adapters (89 tests passing)

### Backend — Debate Orchestrator
- [x] Implement session management (in-memory sessions)
- [x] Build prompt construction system (system prompt, history, persona)
- [x] Implement round-robin turn management
- [x] Wire up WebSocket events (debate:start, turn_start, token_stream, turn_end)
- [x] Add manual termination (debate:stop)

### Backend — API Routes
- [x] POST `/api/keys/validate` — Key validation endpoint
- [x] GET `/api/keys/providers` — Provider listing endpoint

### Frontend — API Key Panel
- [x] Build API key input form (all 8 providers)
- [x] Integrate server-side key validation
- [x] Store keys in sessionStorage
- [x] Show validation status per provider (green check / red X / spinner)
- [x] Masked inputs with show/hide toggle

### Frontend — Topic Input & Config
- [x] Build topic text input
- [x] Build config panel (max rounds, temperature, max tokens, consensus threshold)
- [x] Build participant selection (dynamic, based on validated keys)
- [x] Persona/role assignment per participant
- [x] "Begin Debate" button (requires topic + ≥2 participants)

### Frontend — Debate Viewer
- [x] Transcript view with speaker labels and provider colors
- [x] Streaming text display (token batching at ~20fps)
- [x] Round counter and round dividers
- [x] Pause/Resume/Stop controls
- [x] Auto-scroll with manual override (scroll-lock on manual scroll)
- [x] Error banner for connection/speaker errors

### Integration & Testing
- [ ] End-to-end test: 2 LLMs debate a topic with streaming
- [ ] Error handling: invalid key, API timeout, rate limit
- [ ] Basic README with setup instructions

---

## Phase 2: Multi-LLM & Consensus

### Backend — Additional Adapters
- [x] Implement Gemini adapter with streaming
- [x] Implement xAI/Grok adapter (OpenAI-compatible) with streaming
- [x] Implement DeepSeek adapter (placeholder, OpenAI-compatible)
- [x] Implement Kimi/Moonshot adapter (placeholder, OpenAI-compatible)
- [x] Implement Qwen/Alibaba adapter (placeholder, OpenAI-compatible)
- [x] Implement GLM/Zhipu adapter (placeholder, OpenAI-compatible)
- [x] Write unit tests for all adapters (89 tests)

### Backend — Consensus Detection
- [x] Implement explicit agreement marker detection
- [x] Implement position extraction via LLM call
- [x] Implement stagnation detection
- [x] Build composite consensus scoring
- [x] Integrate consensus check into orchestrator loop

### Backend — Conspectus Generator
- [x] Build conspectus prompt template
- [x] Implement summary generation using available LLM
- [x] Return structured conspectus to frontend

### Frontend — Full Configuration
- [x] Full participant selection for 8 providers
- [x] Temperature, max tokens, consensus threshold sliders
- [x] Persona/role assignment UI
- [x] Token usage display per speaker
- [ ] Estimated cost tracking in UI

### Frontend — Consensus & Conspectus
- [x] Consensus meter component (animated progress bar with color coding)
- [x] Consensus check display after each round (agreed/contested points)
- [x] Consensus history mini-chart
- [x] Conspectus display view (rendered markdown)
- [x] Copy conspectus to clipboard
- [ ] Export transcript/conspectus as downloadable Markdown file

---

## Phase 3: Agora Theme & UX Polish

- [x] Design Agora visual theme (marble, sand, stone, bronze, gold, olive, terracotta palette)
- [x] Greek-inspired typography (Cinzel display + Inter body)
- [x] Provider-specific color scheme for all 8 providers
- [x] Animated consensus meter with Framer Motion transitions
- [x] Toast notification system (success/error/info)
- [x] Loading states and typing indicators (bouncing dots)
- [x] Responsive design (grid layout)
- [ ] Amphitheater-style layout enhancements
- [ ] Debate timeline / round navigator
- [ ] Preset topic suggestions
- [ ] PDF export option

---

## Phase 4: Advanced Features

- [ ] Debate modes: Socratic, Oxford-style, free-form
- [ ] User participation (user as a debate participant)
- [ ] Local debate history (localStorage)
- [ ] Shareable debate links
- [ ] Pre-debate cost estimator
- [ ] Additional providers: Mistral, Cohere, Llama
- [ ] Accessibility audit and improvements
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] Cloud deployment (Vercel + Railway/Fly.io)
- [ ] Monitoring and error tracking (Sentry)

---

## Notes

- API keys are NEVER persisted — in-memory only, purged on session end
- All LLM calls go through the backend (server-side routing)
- Debate flow is structured rounds (round-robin) for all phases
- 8 providers supported: Anthropic, OpenAI, Google, xAI, DeepSeek, Kimi, Qwen, GLM
- xAI/Grok, DeepSeek, Kimi, Qwen, GLM all use OpenAI-compatible APIs
- Number of speakers is dynamic based on validated API keys (minimum 2)
