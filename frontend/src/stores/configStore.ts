import { create } from "zustand";
import type { Participant, Provider } from "@/types";

interface ConfigStore {
  topic: string;
  participants: Participant[];
  maxRounds: number;
  maxTokensPerTurn: number;
  consensusThreshold: number;
  moderatorIndex: number;

  setTopic: (topic: string) => void;
  addParticipant: (participant: Participant) => void;
  removeParticipant: (index: number) => void;
  updateParticipant: (index: number, updates: Partial<Participant>) => void;
  setMaxRounds: (value: number) => void;
  setMaxTokensPerTurn: (value: number) => void;
  setConsensusThreshold: (value: number) => void;
  setModeratorIndex: (index: number) => void;
  canStartDebate: () => boolean;
  getUniqueProviders: () => Provider[];
  reset: () => void;
}

export const useConfigStore = create<ConfigStore>((set, get) => ({
  topic: "",
  participants: [],
  maxRounds: 10,
  maxTokensPerTurn: 1024,
  consensusThreshold: 0.8,
  moderatorIndex: 0,

  setTopic: (topic) => set({ topic }),

  addParticipant: (participant) =>
    set((state) => ({
      participants: [...state.participants, participant],
    })),

  removeParticipant: (index) =>
    set((state) => {
      const newParticipants = state.participants.filter((_, i) => i !== index);
      // Adjust moderator index if needed
      let newModeratorIndex = state.moderatorIndex;
      if (index < state.moderatorIndex) {
        newModeratorIndex--;
      } else if (index === state.moderatorIndex) {
        newModeratorIndex = 0;
      }
      if (newModeratorIndex >= newParticipants.length) {
        newModeratorIndex = 0;
      }
      return { participants: newParticipants, moderatorIndex: newModeratorIndex };
    }),

  updateParticipant: (index, updates) =>
    set((state) => ({
      participants: state.participants.map((p, i) =>
        i === index ? { ...p, ...updates } : p
      ),
    })),

  setMaxRounds: (maxRounds) => set({ maxRounds }),
  setMaxTokensPerTurn: (maxTokensPerTurn) => set({ maxTokensPerTurn }),
  setConsensusThreshold: (consensusThreshold) => set({ consensusThreshold }),
  setModeratorIndex: (moderatorIndex) => set({ moderatorIndex }),

  canStartDebate: () => {
    const { topic, participants } = get();
    return topic.trim().length > 0 && participants.length >= 2;
  },

  getUniqueProviders: () => {
    const { participants } = get();
    return [...new Set(participants.map((p) => p.provider))];
  },

  reset: () =>
    set({
      topic: "",
      participants: [],
      maxRounds: 10,
      maxTokensPerTurn: 1024,
      consensusThreshold: 0.8,
      moderatorIndex: 0,
    }),
}));
