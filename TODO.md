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
- [ ] Initialize monorepo structure (`frontend/` + `backend/`)
- [ ] Set up React project with Vite + TypeScript + Tailwind CSS
- [ ] Set up FastAPI project with project structure
- [ ] Configure linting and formatting (ESLint, Prettier, Ruff)
- [ ] Set up Socket.IO on both frontend and backend
- [ ] Create basic dev environment documentation in README

---

## Phase 1: Foundation & MVP

### Backend — LLM Adapters
- [ ] Define abstract `LLMAdapter` base class
- [ ] Implement Anthropic (Claude) adapter with streaming
- [ ] Implement OpenAI (GPT) adapter with streaming
- [ ] Write unit tests for both adapters

### Backend — Debate Orchestrator
- [ ] Implement session management (in-memory sessions)
- [ ] Build prompt construction system (system prompt, history, persona)
- [ ] Implement round-robin turn management
- [ ] Wire up WebSocket events (debate:start, turn_start, token_stream, turn_end)
- [ ] Add manual termination (debate:stop)

### Backend — API Routes
- [ ] POST `/api/keys/validate` — Key validation endpoint

### Frontend — API Key Panel
- [ ] Build API key input form (Anthropic, OpenAI fields)
- [ ] Add client-side key format validation
- [ ] Integrate server-side key validation
- [ ] Store keys in sessionStorage
- [ ] Show validation status per provider

### Frontend — Topic Input & Config
- [ ] Build topic text input
- [ ] Build basic config panel (max rounds)
- [ ] Build participant selection (based on valid keys)
- [ ] "Begin Debate" button triggering WebSocket connection

### Frontend — Debate Viewer (Basic)
- [ ] Transcript view with speaker labels and colors
- [ ] Streaming text display (token-by-token)
- [ ] Round counter
- [ ] Stop button
- [ ] Auto-scroll with manual override

### Integration & Testing
- [ ] End-to-end test: 2 LLMs debate a topic with streaming
- [ ] Error handling: invalid key, API timeout, rate limit
- [ ] Basic README with setup instructions

---

## Phase 2: Multi-LLM & Consensus

### Backend — Additional Adapters
- [ ] Implement Gemini adapter with streaming
- [ ] Implement xAI/Grok adapter (OpenAI-compatible) with streaming
- [ ] Write unit tests for new adapters

### Backend — Consensus Detection
- [ ] Implement explicit agreement marker detection
- [ ] Implement position extraction via LLM call
- [ ] Implement stagnation detection
- [ ] Build composite consensus scoring
- [ ] Integrate consensus check into orchestrator loop

### Backend — Conspectus Generator
- [ ] Build conspectus prompt template
- [ ] Implement summary generation using available LLM
- [ ] Return structured conspectus to frontend

### Frontend — Full Configuration
- [ ] Full participant selection for 4 providers
- [ ] Temperature, max tokens, consensus threshold sliders
- [ ] Persona/role assignment UI
- [ ] Token usage display per speaker
- [ ] Estimated cost tracking

### Frontend — Consensus & Conspectus
- [ ] Consensus meter component (progress bar with score)
- [ ] Consensus check event display after each round
- [ ] Conspectus display view (structured summary)
- [ ] Export transcript/conspectus as Markdown

---

## Phase 3: Agora Theme & UX Polish

- [ ] Design Agora visual theme (color palette, typography, textures)
- [ ] Amphitheater-style layout for debate viewer
- [ ] Speaker avatars and visual identities per provider
- [ ] Animated consensus meter with transitions
- [ ] Debate timeline / round navigator
- [ ] Responsive design (mobile-friendly)
- [ ] Toast notifications for errors and state changes
- [ ] Loading states and typing indicators
- [ ] Preset topic suggestions
- [ ] PDF export option

---

## Phase 4: Advanced Features

- [ ] Debate modes: Socratic, Oxford-style, free-form
- [ ] User participation (user as a debate participant)
- [ ] Local debate history (localStorage)
- [ ] Shareable debate links
- [ ] Pre-debate cost estimator
- [ ] Additional providers: Mistral, Cohere, DeepSeek, Llama
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
- xAI/Grok uses OpenAI-compatible API, so it shares the OpenAI SDK
