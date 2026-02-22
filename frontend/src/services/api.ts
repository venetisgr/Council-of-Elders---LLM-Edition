import type { Provider, KeyValidationResult } from "@/types";

const API_BASE = "/api";

export async function healthCheck(): Promise<{ status: string; app: string }> {
  const res = await fetch("/health");
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}

export async function validateKey(
  provider: Provider,
  apiKey: string
): Promise<KeyValidationResult> {
  const res = await fetch(`${API_BASE}/keys/validate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ provider, api_key: apiKey }),
  });
  if (!res.ok) throw new Error(`Validation failed: ${res.status}`);
  return res.json();
}

export async function fetchProviders(): Promise<
  Record<string, string[]>
> {
  const res = await fetch(`${API_BASE}/keys/providers`);
  if (!res.ok) throw new Error(`Fetch providers failed: ${res.status}`);
  const data = await res.json();
  return data.providers;
}
