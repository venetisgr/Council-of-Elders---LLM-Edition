import { useState } from "react";
import { Eye, EyeOff, CheckCircle, XCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/common/Button";
import { useKeyStore } from "@/stores/keyStore";
import type { Provider } from "@/types";
import type { ProviderInfo } from "@/types/providers";

interface ApiKeyInputProps {
  provider: ProviderInfo;
}

export function ApiKeyInput({ provider }: ApiKeyInputProps) {
  const [visible, setVisible] = useState(false);
  const { keys, setKey, validateKey, clearKey } = useKeyStore();
  const keyState = keys[provider.id];
  const currentKey = keyState?.key ?? "";
  const valid = keyState?.valid ?? null;
  const validating = keyState?.validating ?? false;

  const handleValidate = () => {
    if (currentKey.trim()) {
      validateKey(provider.id as Provider);
    }
  };

  return (
    <div className="flex items-center gap-3">
      {/* Provider color indicator */}
      <div
        className="w-3 h-3 rounded-full flex-shrink-0"
        style={{ backgroundColor: provider.color }}
      />

      {/* Provider name */}
      <span className="w-20 text-sm font-medium text-ink flex-shrink-0">
        {provider.displayName}
      </span>

      {/* Key input */}
      <div className="relative flex-1">
        <input
          type={visible ? "text" : "password"}
          value={currentKey}
          onChange={(e) => setKey(provider.id as Provider, e.target.value)}
          placeholder={`Enter ${provider.displayName} API key...`}
          className="w-full rounded-lg border border-stone/30 bg-white px-3 py-2 pr-10
            text-sm text-ink placeholder:text-stone/50
            focus:border-bronze focus:outline-none focus:ring-1 focus:ring-bronze/30"
        />
        <button
          type="button"
          onClick={() => setVisible(!visible)}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-stone hover:text-ink"
        >
          {visible ? (
            <EyeOff className="h-4 w-4" />
          ) : (
            <Eye className="h-4 w-4" />
          )}
        </button>
      </div>

      {/* Validate button */}
      <Button
        variant="secondary"
        onClick={handleValidate}
        disabled={!currentKey.trim() || validating}
        loading={validating}
        className="text-xs px-3 py-1.5"
      >
        Validate
      </Button>

      {/* Status indicator */}
      <div className="w-6 flex-shrink-0 flex justify-center">
        {validating ? (
          <Loader2 className="h-5 w-5 text-bronze animate-spin" />
        ) : valid === true ? (
          <CheckCircle className="h-5 w-5 text-olive" />
        ) : valid === false ? (
          <XCircle className="h-5 w-5 text-terracotta" />
        ) : null}
      </div>

      {/* Clear button */}
      {currentKey && (
        <button
          onClick={() => clearKey(provider.id as Provider)}
          className="text-xs text-stone hover:text-terracotta"
        >
          Clear
        </button>
      )}
    </div>
  );
}
