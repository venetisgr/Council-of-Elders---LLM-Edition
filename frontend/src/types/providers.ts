import { Provider } from "./index";

export interface ProviderInfo {
  id: Provider;
  displayName: string;
  color: string;
  defaultModel: string;
  description: string;
}

export const PROVIDERS: ProviderInfo[] = [
  {
    id: Provider.ANTHROPIC,
    displayName: "Claude",
    color: "#D97706",
    defaultModel: "claude-opus-4-6",
    description: "Anthropic's Claude models",
  },
  {
    id: Provider.OPENAI,
    displayName: "OpenAI",
    color: "#10B981",
    defaultModel: "gpt-5.2",
    description: "OpenAI's GPT models",
  },
  {
    id: Provider.GOOGLE,
    displayName: "Gemini",
    color: "#3B82F6",
    defaultModel: "gemini-3-pro-preview",
    description: "Google's Gemini models",
  },
  {
    id: Provider.XAI,
    displayName: "Grok",
    color: "#8B5CF6",
    defaultModel: "grok-3",
    description: "xAI's Grok models",
  },
  {
    id: Provider.DEEPSEEK,
    displayName: "DeepSeek",
    color: "#06B6D4",
    defaultModel: "deepseek-chat",
    description: "DeepSeek AI models",
  },
  {
    id: Provider.KIMI,
    displayName: "Kimi",
    color: "#EC4899",
    defaultModel: "moonshot-v1-128k",
    description: "Moonshot's Kimi models",
  },
  {
    id: Provider.QWEN,
    displayName: "Qwen",
    color: "#F97316",
    defaultModel: "qwen3-max",
    description: "Alibaba's Qwen models",
  },
  {
    id: Provider.GLM,
    displayName: "GLM",
    color: "#EF4444",
    defaultModel: "glm-5",
    description: "Zhipu's GLM models",
  },
];

export function getProviderInfo(provider: Provider): ProviderInfo {
  return PROVIDERS.find((p) => p.id === provider) ?? PROVIDERS[0]!;
}

export function getProviderColor(provider: Provider): string {
  return getProviderInfo(provider).color;
}
