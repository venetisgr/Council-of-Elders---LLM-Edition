import { create } from "zustand";
import type { Socket } from "socket.io-client";
import type {
  DebateMessage,
  ConsensusCheck,
  DebateStatus,
  DebateConfig,
  Provider,
} from "@/types";
import type {
  DebateStartedPayload,
  RoundStartPayload,
  TurnStartPayload,
  TokenStreamPayload,
  TurnEndPayload,
  ConsensusCheckPayload,
  ConcludedPayload,
  ConspectusPayload,
  DebateErrorPayload,
} from "@/types/events";
import { connectSocket, disconnectSocket } from "@/services/socket";

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

export const useDebateStore = create<DebateStore>((set, get) => {
  let socket: Socket | null = null;

  function flushTokens(): void {
    const buffered = { ...tokenBuffer };
    tokenBuffer = {};
    const hasPending = Object.keys(buffered).length > 0;
    if (!hasPending) return;

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

  function attachListeners(s: Socket): void {
    s.on("debate:started", (data: DebateStartedPayload) => {
      set({
        status: "running" as DebateStatus,
        sessionId: data.session_id,
        error: null,
      });
    });

    s.on("debate:round_start", (data: RoundStartPayload) => {
      set({ currentRound: data.round });
    });

    s.on("debate:turn_start", (data: TurnStartPayload) => {
      set((state) => ({
        currentSpeaker: data.speaker,
        transcript: [
          ...state.transcript,
          {
            speaker: data.speaker,
            provider: data.provider,
            model: "",
            content: "",
            round_number: data.round,
            token_count: 0,
            isStreaming: true,
          },
        ],
      }));
      startTokenFlushing(flushTokens);
    });

    s.on("debate:token_stream", (data: TokenStreamPayload) => {
      // Accumulate in buffer instead of updating state directly
      tokenBuffer[data.speaker] =
        (tokenBuffer[data.speaker] ?? "") + data.token;
    });

    s.on("debate:turn_end", (data: TurnEndPayload) => {
      // Final flush for this speaker
      flushTokens();
      set((state) => {
        const transcript = [...state.transcript];
        const lastIdx = transcript.length - 1;
        const last = transcript[lastIdx];
        if (last && last.speaker === data.speaker) {
          transcript[lastIdx] = {
            ...last,
            isStreaming: false,
            token_count: data.token_count,
          };
        }
        return { transcript, currentSpeaker: null };
      });
    });

    s.on("debate:consensus_check", (data: ConsensusCheckPayload) => {
      set((state) => ({
        consensusHistory: [
          ...state.consensusHistory,
          {
            round: data.round,
            consensus_score: data.consensus_score,
            stagnation_detected: data.stagnation_detected,
            agreed_points: data.agreed_points,
            contested_points: data.contested_points,
            summary: data.summary,
          },
        ],
      }));
    });

    s.on("debate:concluded", (data: ConcludedPayload) => {
      stopTokenFlushing();
      set({
        status: "concluded" as DebateStatus,
        tokenUsage: data.token_usage,
        currentRound: data.total_rounds,
      });
    });

    s.on("debate:generating_conspectus", () => {
      set({ generatingConspectus: true });
    });

    s.on("debate:conspectus", (data: ConspectusPayload) => {
      set({
        conspectus: data.conspectus,
        generatingConspectus: false,
      });
    });

    s.on("debate:paused", () => {
      set({ status: "paused" as DebateStatus });
    });

    s.on("debate:resumed", () => {
      set({ status: "running" as DebateStatus });
    });

    s.on("debate:stopped", () => {
      stopTokenFlushing();
      set({ status: "concluded" as DebateStatus });
    });

    s.on("debate:error", (data: DebateErrorPayload) => {
      if (data.speaker) {
        // Non-fatal: one speaker errored, show inline
        set((state) => ({
          transcript: [
            ...state.transcript,
            {
              speaker: data.speaker!,
              provider: "anthropic" as Provider, // Fallback, displayed as error
              model: "",
              content: `[Error: ${data.error}]`,
              round_number: data.round ?? state.currentRound,
              token_count: 0,
            },
          ],
        }));
      } else {
        // Fatal error
        stopTokenFlushing();
        set({
          status: "error" as DebateStatus,
          error: data.error,
        });
      }
    });

    s.on("disconnect", () => {
      const { status } = get();
      if (status === "running" || status === "paused") {
        set({ error: "Connection lost. Attempting to reconnect..." });
      }
    });

    s.on("connect", () => {
      const { error } = get();
      if (error?.includes("reconnect")) {
        set({ error: null });
      }
    });
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

      tokenBuffer = {};
      socket = connectSocket();
      attachListeners(socket);

      socket.emit("debate:start", {
        topic: config.topic,
        participants: config.participants,
        api_keys: apiKeys,
        max_rounds: config.max_rounds,
        max_tokens_per_turn: config.max_tokens_per_turn,
        temperature: config.temperature,
        consensus_threshold: config.consensus_threshold,
      });
    },

    pauseDebate: () => {
      const { sessionId } = get();
      if (socket && sessionId) {
        socket.emit("debate:pause", { session_id: sessionId });
      }
    },

    resumeDebate: () => {
      const { sessionId } = get();
      if (socket && sessionId) {
        socket.emit("debate:resume", { session_id: sessionId });
      }
    },

    stopDebate: () => {
      const { sessionId } = get();
      if (socket && sessionId) {
        socket.emit("debate:stop", { session_id: sessionId });
      }
    },

    reset: () => {
      stopTokenFlushing();
      tokenBuffer = {};
      disconnectSocket();
      socket = null;
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
