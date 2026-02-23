/**
 * HTTP/SSE-based debate service.
 *
 * Replaces Socket.IO for Vercel-compatible serverless debate streaming.
 * Each function maps to a single backend endpoint and fits within
 * Vercel's serverless function timeout.
 */

import type { Participant } from "@/types";
import { getBackendUrl } from "./api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface TurnParams {
  topic: string;
  participant: Participant;
  transcript: Array<{ speaker: string; content: string }>;
  api_key: string;
  max_tokens: number;
  temperature: number;
}

export interface TurnResult {
  content: string;
  token_count: number;
}

export interface ConsensusParams {
  topic: string;
  round_transcript: Array<{ speaker: string; content: string }>;
  previous_round_responses: string[] | null;
  adapter_provider?: string;
  adapter_model?: string;
  adapter_api_key?: string;
}

export interface ConsensusResult {
  consensus_score: number;
  stagnation_detected: boolean;
  agreed_points: string[];
  contested_points: string[];
  summary: string;
}

export interface ConspectusParams {
  topic: string;
  transcript: Array<{ speaker: string; content: string; round?: number }>;
  participants: string[];
  rounds: number;
  consensus_score: number;
  provider: string;
  model: string;
  api_key: string;
}

// ---------------------------------------------------------------------------
// SSE stream reader
// ---------------------------------------------------------------------------

async function readSSEStream(
  response: Response,
  onToken: (token: string) => void
): Promise<{ content: string; token_count: number }> {
  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finalContent = "";
  let finalTokenCount = 0;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    // Keep the last (possibly incomplete) line in the buffer
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (!line.startsWith("data: ")) continue;
      const json_str = line.slice(6);
      if (!json_str) continue;

      try {
        const event = JSON.parse(json_str);
        if (event.type === "token") {
          onToken(event.content);
        } else if (event.type === "done") {
          finalContent = event.content;
          finalTokenCount = event.token_count ?? 0;
        } else if (event.type === "error") {
          throw new Error(event.error);
        }
      } catch (e) {
        if (e instanceof SyntaxError) continue; // Skip malformed JSON
        throw e;
      }
    }
  }

  return { content: finalContent, token_count: finalTokenCount };
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

const BASE = () => `${getBackendUrl()}/api/debate`;

/**
 * Stream one participant's turn.  Calls `onToken` for each streamed token.
 * Returns the full content and approximate token count when done.
 */
export async function streamTurn(
  params: TurnParams,
  onToken: (token: string) => void,
  signal?: AbortSignal
): Promise<TurnResult> {
  const res = await fetch(`${BASE()}/turn`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
    signal,
  });
  if (!res.ok) throw new Error(`Turn request failed: ${res.status}`);
  return readSSEStream(res, onToken);
}

/**
 * Check consensus after a complete round.
 */
export async function checkConsensus(
  params: ConsensusParams,
  signal?: AbortSignal
): Promise<ConsensusResult> {
  const res = await fetch(`${BASE()}/consensus`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
    signal,
  });
  if (!res.ok) throw new Error(`Consensus request failed: ${res.status}`);
  return res.json();
}

/**
 * Generate the final conspectus, streamed token-by-token.
 */
export async function streamConspectus(
  params: ConspectusParams,
  onToken: (token: string) => void,
  signal?: AbortSignal
): Promise<string> {
  const res = await fetch(`${BASE()}/conspectus`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(params),
    signal,
  });
  if (!res.ok) throw new Error(`Conspectus request failed: ${res.status}`);
  const result = await readSSEStream(res, onToken);
  return result.content;
}
