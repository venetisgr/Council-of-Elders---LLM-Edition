export enum Provider {
  ANTHROPIC = "anthropic",
  OPENAI = "openai",
  GOOGLE = "google",
  XAI = "xai",
  DEEPSEEK = "deepseek",
  KIMI = "kimi",
  QWEN = "qwen",
  GLM = "glm",
}

export enum DebateStatus {
  IDLE = "idle",
  PENDING = "pending",
  RUNNING = "running",
  PAUSED = "paused",
  CONCLUDED = "concluded",
  ERROR = "error",
}

export interface Participant {
  provider: Provider;
  model: string;
  display_name: string;
  persona: string;
}

export interface DebateConfig {
  topic: string;
  participants: Participant[];
  max_rounds: number;
  max_tokens_per_turn: number;
  temperature: number;
  consensus_threshold: number;
}

export interface DebateMessage {
  speaker: string;
  provider: Provider;
  model: string;
  content: string;
  round_number: number;
  token_count: number;
  isStreaming?: boolean;
}

export interface ConsensusCheck {
  round: number;
  consensus_score: number;
  stagnation_detected: boolean;
  agreed_points: string[];
  contested_points: string[];
  summary: string;
}

export interface KeyValidationResult {
  provider: Provider;
  valid: boolean;
  message: string;
  available_models: string[];
}

export interface KeyState {
  key: string;
  valid: boolean | null;
  validating: boolean;
  models: string[];
}
