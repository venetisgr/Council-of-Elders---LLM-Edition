import { create } from "zustand";
import type {
  DebateMessage,
  ConsensusCheck,
  DebateStatus,
  DebateConfig,
} from "@/types";
import {
  streamTurn,
  checkConsensus,
  streamConspectus,
} from "@/services/debate";

interface DebateStore {
  status: DebateStatus;
  sessionId: string | null;
  currentRound: number;
  currentSpeaker: string | null;
  transcript: DebateMessage[];
  consensusHistory: ConsensusCheck[];
  tokenUsage: Record<string, number>;
  conspectus: string | null;
  generatingConspectus: boolean;
  error: string | null;

  startDebate: (config: DebateConfig, apiKeys: Record<string, string>) => void;
  pauseDebate: () => void;
  resumeDebate: () => void;
  stopDebate: () => void;
  reset: () => void;
}

// Token batching: accumulate streaming tokens and flush periodically
let tokenBuffer: Record<string, string> = {};
let flushTimer: ReturnType<typeof setInterval> | null = null;

function startTokenFlushing(flush: () => void): void {
  if (flushTimer) return;
  flushTimer = setInterval(flush, 50); // ~20 fps
}

function stopTokenFlushing(): void {
  if (flushTimer) {
    clearInterval(flushTimer);
    flushTimer = null;
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((r) => setTimeout(r, ms));
}

export const useDebateStore = create<DebateStore>((set, get) => {
  // Mutable loop-control flags (outside Zustand state to avoid async issues)
  let _paused = false;
  let _stopped = false;
  let _abortController: AbortController | null = null;

  function flushTokens(): void {
    const buffered = { ...tokenBuffer };
    tokenBuffer = {};
    if (Object.keys(buffered).length === 0) return;

    set((state) => {
      const transcript = [...state.transcript];
      for (const [speaker, tokens] of Object.entries(buffered)) {
        const lastIdx = transcript.length - 1;
        const last = transcript[lastIdx];
        if (last && last.speaker === speaker && last.isStreaming) {
          transcript[lastIdx] = {
            ...last,
            content: last.content + tokens,
          };
        }
      }
      return { transcript };
    });
  }

  /**
   * The core debate loop.  Runs entirely in the frontend, making
   * sequential HTTP calls to the serverless backend endpoints.
   */
  async function runDebateLoop(
    config: DebateConfig,
    apiKeys: Record<string, string>
  ): Promise<void> {
    const sessionId = crypto.randomUUID();
    set({
      status: "running" as DebateStatus,
      sessionId,
      error: null,
    });

    let previousRoundResponses: string[] | null = null;
    let stagnationCount = 0;
    const tokenUsage: Record<string, number> = {};

    for (let round = 1; round <= config.max_rounds; round++) {
      if (_stopped) break;

      set({ currentRound: round });

      const roundResponses: string[] = [];
      const roundTranscript: Array<{ speaker: string; content: string }> = [];

      // Each participant takes a turn
      for (const participant of config.participants) {
        // Wait while paused
        while (_paused && !_stopped) {
          set({ status: "paused" as DebateStatus });
          await sleep(500);
        }
        if (_stopped) break;
        if (get().status === "paused") {
          set({ status: "running" as DebateStatus });
        }

        // Add streaming message placeholder
        set((state) => ({
          currentSpeaker: participant.display_name,
          transcript: [
            ...state.transcript,
            {
              speaker: participant.display_name,
              provider: participant.provider,
              model: participant.model,
              content: "",
              round_number: round,
              token_count: 0,
              isStreaming: true,
            },
          ],
        }));

        startTokenFlushing(flushTokens);

        try {
          // Build the transcript for context (all previous complete messages)
          const contextTranscript = get()
            .transcript.filter((m) => !m.isStreaming)
            .map((m) => ({ speaker: m.speaker, content: m.content }));

          const result = await streamTurn(
            {
              topic: config.topic,
              participant,
              transcript: contextTranscript,
              api_key: apiKeys[participant.provider] ?? "",
              max_tokens: config.max_tokens_per_turn,
              temperature: config.temperature,
            },
            (token) => {
              tokenBuffer[participant.display_name] =
                (tokenBuffer[participant.display_name] ?? "") + token;
            },
            _abortController?.signal
          );

          // Final flush + finalize message
          flushTokens();
          stopTokenFlushing();

          set((state) => {
            const transcript = [...state.transcript];
            const lastIdx = transcript.length - 1;
            transcript[lastIdx] = {
              ...transcript[lastIdx],
              content: result.content,
              isStreaming: false,
              token_count: result.token_count,
            };
            return { transcript, currentSpeaker: null };
          });

          tokenUsage[participant.display_name] =
            (tokenUsage[participant.display_name] ?? 0) + result.token_count;

          roundResponses.push(result.content);
          roundTranscript.push({
            speaker: participant.display_name,
            content: result.content,
          });
        } catch (err) {
          flushTokens();
          stopTokenFlushing();

          // AbortError means the user clicked Stop
          if (err instanceof DOMException && err.name === "AbortError") {
            _stopped = true;
            break;
          }

          // Non-fatal: show error in transcript and continue
          const msg = err instanceof Error ? err.message : String(err);
          set((state) => {
            const transcript = [...state.transcript];
            const lastIdx = transcript.length - 1;
            if (transcript[lastIdx]?.isStreaming) {
              transcript[lastIdx] = {
                ...transcript[lastIdx],
                content: `[Error: ${msg}]`,
                isStreaming: false,
              };
            }
            return { transcript, currentSpeaker: null };
          });
        }
      }

      if (_stopped) break;

      // Consensus check after each round
      try {
        const firstParticipant = config.participants[0];
        const consensus = await checkConsensus(
          {
            topic: config.topic,
            round_transcript: roundTranscript,
            previous_round_responses: previousRoundResponses,
            adapter_provider: firstParticipant?.provider,
            adapter_model: firstParticipant?.model,
            adapter_api_key: firstParticipant
              ? apiKeys[firstParticipant.provider]
              : undefined,
          },
          _abortController?.signal
        );

        set((state) => ({
          consensusHistory: [
            ...state.consensusHistory,
            {
              round,
              consensus_score: consensus.consensus_score,
              stagnation_detected: consensus.stagnation_detected,
              agreed_points: consensus.agreed_points ?? [],
              contested_points: consensus.contested_points ?? [],
              summary: consensus.summary ?? "",
            },
          ],
        }));

        // Termination conditions
        if (consensus.consensus_score >= config.consensus_threshold) break;
        if (consensus.stagnation_detected) {
          stagnationCount++;
          if (stagnationCount >= 3) break;
        } else {
          stagnationCount = 0;
        }
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") break;
        console.error("Consensus check failed:", err);
      }

      previousRoundResponses = roundResponses;
    }

    // Debate concluded
    set({
      status: "concluded" as DebateStatus,
      tokenUsage,
      currentSpeaker: null,
    });

    // Generate conspectus
    if (get().transcript.length > 0) {
      try {
        set({ generatingConspectus: true });

        const firstParticipant = config.participants[0];
        if (!firstParticipant) throw new Error("No participants");

        const history = get().consensusHistory;
        const finalScore =
          history.length > 0 ? history[history.length - 1].consensus_score : 0;

        const conspectus = await streamConspectus(
          {
            topic: config.topic,
            transcript: get().transcript.map((m) => ({
              speaker: m.speaker,
              content: m.content,
              round: m.round_number,
            })),
            participants: config.participants.map((p) => p.display_name),
            rounds: get().currentRound,
            consensus_score: finalScore,
            provider: firstParticipant.provider,
            model: firstParticipant.model,
            api_key: apiKeys[firstParticipant.provider] ?? "",
          },
          () => {
            /* tokens handled by streamConspectus; set all at once */
          }
        );

        set({ conspectus, generatingConspectus: false });
      } catch {
        set({ generatingConspectus: false });
      }
    }
  }

  return {
    status: "idle" as DebateStatus,
    sessionId: null,
    currentRound: 0,
    currentSpeaker: null,
    transcript: [],
    consensusHistory: [],
    tokenUsage: {},
    conspectus: null,
    generatingConspectus: false,
    error: null,

    startDebate: (config, apiKeys) => {
      set({
        status: "pending" as DebateStatus,
        sessionId: null,
        currentRound: 0,
        currentSpeaker: null,
        transcript: [],
        consensusHistory: [],
        tokenUsage: {},
        conspectus: null,
        generatingConspectus: false,
        error: null,
      });

      _paused = false;
      _stopped = false;
      _abortController = new AbortController();
      tokenBuffer = {};

      // Fire-and-forget the async debate loop
      runDebateLoop(config, apiKeys).catch((err) => {
        stopTokenFlushing();
        set({
          status: "error" as DebateStatus,
          error: err instanceof Error ? err.message : String(err),
        });
      });
    },

    pauseDebate: () => {
      _paused = true;
    },

    resumeDebate: () => {
      _paused = false;
    },

    stopDebate: () => {
      _stopped = true;
      _abortController?.abort();
      stopTokenFlushing();
      set({
        status: "concluded" as DebateStatus,
        currentSpeaker: null,
      });
    },

    reset: () => {
      _stopped = true;
      _paused = false;
      _abortController?.abort();
      _abortController = null;
      stopTokenFlushing();
      tokenBuffer = {};
      set({
        status: "idle" as DebateStatus,
        sessionId: null,
        currentRound: 0,
        currentSpeaker: null,
        transcript: [],
        consensusHistory: [],
        tokenUsage: {},
        conspectus: null,
        generatingConspectus: false,
        error: null,
      });
    },
  };
});
