import { useEffect, useState } from "react";
import { KeyRound, AlertTriangle } from "lucide-react";
import { ApiKeyInput } from "./ApiKeyInput";
import { Button } from "@/components/common/Button";
import { useKeyStore } from "@/stores/keyStore";
import { PROVIDERS } from "@/types/providers";
import { healthCheck } from "@/services/api";

export function ApiKeyPanel() {
  const { initFromStorage, clearAll, getValidatedProviders } = useKeyStore();
  const validCount = getValidatedProviders().length;
  const [backendDown, setBackendDown] = useState(false);

  useEffect(() => {
    initFromStorage();
  }, [initFromStorage]);

  useEffect(() => {
    healthCheck()
      .then(() => setBackendDown(false))
      .catch(() => setBackendDown(true));
  }, []);

  return (
    <div className="rounded-xl border border-stone/20 bg-white/80 backdrop-blur-sm p-6 shadow-sm">
      {backendDown && (
        <div className="flex items-start gap-2 rounded-lg bg-terracotta/10 px-3 py-2 mb-4">
          <AlertTriangle className="h-4 w-4 text-terracotta flex-shrink-0 mt-0.5" />
          <p className="text-xs text-terracotta">
            Backend not reachable. Start the backend server (<code className="font-mono">uvicorn app.main:socket_app --reload</code>) or set{" "}
            <code className="font-mono">VITE_BACKEND_URL</code> to your deployed backend URL.
          </p>
        </div>
      )}

      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <KeyRound className="h-5 w-5 text-bronze" />
          <h2 className="font-display text-lg text-ink">API Keys</h2>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-stone">
            {validCount} provider{validCount !== 1 ? "s" : ""} validated
          </span>
          <Button variant="ghost" onClick={clearAll} className="text-xs">
            Clear All
          </Button>
        </div>
      </div>

      <p className="text-xs text-stone mb-4">
        Keys are stored in your browser session only and never saved to any
        server. You need at least 2 validated providers to start a debate.
      </p>

      <div className="space-y-3">
        {PROVIDERS.map((provider) => (
          <ApiKeyInput key={provider.id} provider={provider} />
        ))}
      </div>

      {validCount >= 2 && (
        <div className="mt-4 rounded-lg bg-olive/10 px-3 py-2 text-sm text-olive">
          Ready to configure a debate with {validCount} providers.
        </div>
      )}
      {validCount === 1 && (
        <div className="mt-4 rounded-lg bg-bronze/10 px-3 py-2 text-sm text-bronze">
          Add at least one more API key to start a debate.
        </div>
      )}
    </div>
  );
}
