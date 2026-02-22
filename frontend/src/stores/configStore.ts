import { create } from "zustand";
import type { Participant, Provider } from "@/types";

interface ConfigStore {
  topic: string;
  participants: Participant[];
  maxRounds: number;
  maxTokensPerTurn: number;
  temperature: number;
  consensusThreshold: number;

  setTopic: (topic: string) => void;
  addParticipant: (participant: Participant) => void;
  removeParticipant: (index: number) => void;
  updateParticipant: (index: number, updates: Partial<Participant>) => void;
  setMaxRounds: (value: number) => void;
  setMaxTokensPerTurn: (value: number) => void;
  setTemperature: (value: number) => void;
  setConsensusThreshold: (value: number) => void;
  canStartDebate: () => boolean;
  getUniqueProviders: () => Provider[];
  reset: () => void;
}

export const useConfigStore = create<ConfigStore>((set, get) => ({
  topic: "",
  participants: [],
  maxRounds: 10,
  maxTokensPerTurn: 1024,
  temperature: 0.7,
  consensusThreshold: 0.8,

  setTopic: (topic) => set({ topic }),

  addParticipant: (participant) =>
    set((state) => ({
      participants: [...state.participants, participant],
    })),

  removeParticipant: (index) =>
    set((state) => ({
      participants: state.participants.filter((_, i) => i !== index),
    })),

  updateParticipant: (index, updates) =>
    set((state) => ({
      participants: state.participants.map((p, i) =>
        i === index ? { ...p, ...updates } : p
      ),
    })),

  setMaxRounds: (maxRounds) => set({ maxRounds }),
  setMaxTokensPerTurn: (maxTokensPerTurn) => set({ maxTokensPerTurn }),
  setTemperature: (temperature) => set({ temperature }),
  setConsensusThreshold: (consensusThreshold) => set({ consensusThreshold }),

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
      temperature: 0.7,
      consensusThreshold: 0.8,
    }),
}));
