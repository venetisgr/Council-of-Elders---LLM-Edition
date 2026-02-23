import { create } from "zustand";
import type { Provider, KeyState } from "@/types";
import { validateKey as apiValidateKey } from "@/services/api";

const STORAGE_PREFIX = "agora_key_";

function loadKey(provider: Provider): string {
  return sessionStorage.getItem(`${STORAGE_PREFIX}${provider}`) ?? "";
}

function saveKey(provider: Provider, key: string): void {
  if (key) {
    sessionStorage.setItem(`${STORAGE_PREFIX}${provider}`, key);
  } else {
    sessionStorage.removeItem(`${STORAGE_PREFIX}${provider}`);
  }
}

interface KeyStore {
  keys: Record<string, KeyState>;
  setKey: (provider: Provider, key: string) => void;
  validateKey: (provider: Provider) => Promise<void>;
  clearKey: (provider: Provider) => void;
  clearAll: () => void;
  getValidatedProviders: () => Provider[];
  getApiKeys: () => Record<string, string>;
  initFromStorage: () => void;
}

const defaultKeyState = (): KeyState => ({
  key: "",
  valid: null,
  validating: false,
  models: [],
  error: null,
});

export const useKeyStore = create<KeyStore>((set, get) => ({
  keys: {},

  initFromStorage: () => {
    const providers = Object.values(
      // Use the string enum values directly
      {
        anthropic: "anthropic",
        openai: "openai",
        google: "google",
        xai: "xai",
        deepseek: "deepseek",
        kimi: "kimi",
        qwen: "qwen",
        glm: "glm",
      } as Record<string, Provider>
    );
    const keys: Record<string, KeyState> = {};
    for (const p of providers) {
      const stored = loadKey(p);
      keys[p] = { ...defaultKeyState(), key: stored };
    }
    set({ keys });
  },

  setKey: (provider, key) => {
    saveKey(provider, key);
    set((state) => ({
      keys: {
        ...state.keys,
        [provider]: {
          ...(state.keys[provider] ?? defaultKeyState()),
          key,
          valid: null,
          models: [],
          error: null,
        },
      },
    }));
  },

  validateKey: async (provider) => {
    const state = get();
    const keyState = state.keys[provider];
    if (!keyState?.key) return;

    set((s) => ({
      keys: {
        ...s.keys,
        [provider]: { ...keyState, validating: true, error: null },
      },
    }));

    try {
      const result = await apiValidateKey(provider, keyState.key);
      set((s) => ({
        keys: {
          ...s.keys,
          [provider]: {
            key: keyState.key,
            valid: result.valid,
            validating: false,
            models: result.available_models,
            error: result.valid ? null : result.message,
          },
        },
      }));
    } catch (err) {
      let error: string;
      if (err instanceof TypeError) {
        error = "Cannot reach the backend. Is the server running?";
      } else if (err instanceof Error && err.message.includes("405")) {
        error =
          "Backend not connected. Start the backend locally or set VITE_BACKEND_URL.";
      } else if (err instanceof Error) {
        error = err.message;
      } else {
        error = "Validation failed unexpectedly.";
      }
      set((s) => ({
        keys: {
          ...s.keys,
          [provider]: {
            key: keyState.key,
            valid: false,
            validating: false,
            models: [],
            error,
          },
        },
      }));
    }
  },

  clearKey: (provider) => {
    saveKey(provider, "");
    set((state) => ({
      keys: {
        ...state.keys,
        [provider]: defaultKeyState(),
      },
    }));
  },

  clearAll: () => {
    const providers = Object.keys(get().keys);
    for (const p of providers) {
      sessionStorage.removeItem(`${STORAGE_PREFIX}${p}`);
    }
    const keys: Record<string, KeyState> = {};
    for (const p of providers) {
      keys[p] = defaultKeyState();
    }
    set({ keys });
  },

  getValidatedProviders: () => {
    const { keys } = get();
    return Object.entries(keys)
      .filter(([, state]) => state.valid === true)
      .map(([provider]) => provider as Provider);
  },

  getApiKeys: () => {
    const { keys } = get();
    const result: Record<string, string> = {};
    for (const [provider, state] of Object.entries(keys)) {
      if (state.valid && state.key) {
        result[provider] = state.key;
      }
    }
    return result;
  },
}));
