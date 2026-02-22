import type { Provider, KeyValidationResult } from "@/types";

/**
 * In development, Vite proxy handles /api -> backend.
 * In production (Vercel), VITE_BACKEND_URL points to the deployed backend.
 */
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? "";
const API_BASE = `${BACKEND_URL}/api`;

export function getBackendUrl(): string {
  return BACKEND_URL;
}

export async function healthCheck(): Promise<{ status: string; app: string }> {
  const res = await fetch(`${BACKEND_URL}/health`);
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
