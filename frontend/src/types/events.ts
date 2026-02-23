import type { Provider } from "./index";

export interface DebateStartedPayload {
  session_id: string;
  topic: string;
  participants: string[];
}

export interface RoundStartPayload {
  round: number;
}

export interface TurnStartPayload {
  speaker: string;
  provider: Provider;
  round: number;
}

export interface TokenStreamPayload {
  speaker: string;
  token: string;
}

export interface TurnEndPayload {
  speaker: string;
  round: number;
  token_count: number;
}

export interface ConsensusCheckPayload {
  round: number;
  consensus_score: number;
  stagnation_detected: boolean;
  agreed_points: string[];
  contested_points: string[];
  summary: string;
}

export interface ConsensusReachedPayload {
  round: number;
  score: number;
}

export interface StagnationPayload {
  round: number;
  consecutive_stagnation_rounds: number;
}

export interface ConcludedPayload {
  session_id: string;
  total_rounds: number;
  final_consensus: number;
  token_usage: Record<string, number>;
}

export interface ConspectusPayload {
  session_id: string;
  conspectus: string;
}

export interface DebateErrorPayload {
  error: string;
  speaker?: string;
  round?: number;
}

export interface DebatePausedPayload {
  session_id: string;
}

export interface DebateResumedPayload {
  session_id: string;
}

export interface DebateStoppedPayload {
  session_id: string;
}

export interface GeneratingConspectusPayload {
  session_id: string;
}
