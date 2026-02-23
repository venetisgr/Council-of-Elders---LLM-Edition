import { useState } from "react";
import { Plus, Trash2, User, AlertCircle } from "lucide-react";
import { Button } from "@/components/common/Button";
import { useKeyStore } from "@/stores/keyStore";
import { useConfigStore } from "@/stores/configStore";
import { PROVIDERS, getProviderInfo } from "@/types/providers";
import type { Provider } from "@/types";

export function ParticipantSelector() {
  const { keys, getValidatedProviders } = useKeyStore();
  const { participants, addParticipant, removeParticipant, updateParticipant } =
    useConfigStore();

  const validatedProviders = getValidatedProviders();

  const [selectedProvider, setSelectedProvider] = useState<Provider | "">("");
  const [selectedModel, setSelectedModel] = useState("");

  const availableModels =
    selectedProvider && keys[selectedProvider]
      ? keys[selectedProvider].models
      : [];

  const handleAdd = () => {
    if (!selectedProvider || !selectedModel) return;
    const info = getProviderInfo(selectedProvider);
    const baseName = `${info.displayName} (${selectedModel})`;
    // Differentiate duplicate models with a suffix
    const existing = participants.filter(
      (p) => p.provider === selectedProvider && p.model === selectedModel
    ).length;
    const display_name = existing > 0 ? `${baseName} #${existing + 1}` : baseName;
    addParticipant({
      provider: selectedProvider,
      model: selectedModel,
      display_name,
      persona: "",
      temperature: 0.45,
    });
    setSelectedProvider("");
    setSelectedModel("");
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-2">
        <User className="h-4 w-4 text-bronze" />
        <h3 className="text-sm font-semibold text-ink">Participants</h3>
        <span className="text-xs text-stone">
          ({participants.length} selected, min 2)
        </span>
      </div>

      {/* Add participant row */}
      <div className="flex items-center gap-2">
        <select
          value={selectedProvider}
          onChange={(e) => {
            const p = e.target.value as Provider;
            setSelectedProvider(p);
            const providerInfo = PROVIDERS.find((pi) => pi.id === p);
            const providerModels = p && keys[p] ? keys[p].models : [];
            setSelectedModel(
              providerModels[0] ?? providerInfo?.defaultModel ?? ""
            );
          }}
          className="rounded-lg border border-stone/30 bg-white px-3 py-2
            text-sm text-ink focus:border-bronze focus:outline-none"
        >
          <option value="">Select provider...</option>
          {validatedProviders.map((p) => {
            const info = PROVIDERS.find((pi) => pi.id === p);
            return (
              <option key={p} value={p}>
                {info?.displayName ?? p}
              </option>
            );
          })}
        </select>

        {selectedProvider && (
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            className="rounded-lg border border-stone/30 bg-white px-3 py-2
              text-sm text-ink focus:border-bronze focus:outline-none"
          >
            {availableModels.map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>
        )}

        <Button
          variant="secondary"
          onClick={handleAdd}
          disabled={!selectedProvider || !selectedModel}
          className="text-xs"
        >
          <Plus className="h-3.5 w-3.5" />
          Add
        </Button>
      </div>

      {validatedProviders.length === 0 && (
        <div className="flex items-center gap-2 rounded-lg bg-bronze/10 px-3 py-2">
          <AlertCircle className="h-4 w-4 text-bronze flex-shrink-0" />
          <span className="text-xs text-bronze">
            No validated providers yet. Add and validate API keys above to
            select participants.
          </span>
        </div>
      )}

      {/* Participant list */}
      {participants.length > 0 && (
        <div className="space-y-2">
          {participants.map((p, i) => {
            const info = getProviderInfo(p.provider);
            return (
              <div
                key={i}
                className="flex items-center gap-3 rounded-lg bg-sand/30 px-3 py-2"
              >
                <div
                  className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                  style={{ backgroundColor: info.color }}
                />
                <span className="text-sm font-medium text-ink flex-shrink-0">
                  {p.display_name}
                </span>
                <input
                  type="text"
                  value={p.persona}
                  onChange={(e) =>
                    updateParticipant(i, { persona: e.target.value })
                  }
                  placeholder="Optional persona (e.g., 'pragmatist')"
                  className="flex-1 rounded border border-stone/20 bg-white px-2 py-1
                    text-xs text-ink placeholder:text-stone/40
                    focus:border-bronze focus:outline-none"
                />
                <div className="flex items-center gap-1 flex-shrink-0">
                  <label className="text-[10px] text-stone">Temp</label>
                  <input
                    type="number"
                    value={p.temperature}
                    onChange={(e) => {
                      const v = parseFloat(e.target.value);
                      if (!isNaN(v)) updateParticipant(i, { temperature: Math.min(2, Math.max(0, v)) });
                    }}
                    min={0}
                    max={2}
                    step={0.05}
                    className="w-14 rounded border border-stone/20 bg-white px-1.5 py-1
                      text-xs text-ink text-center
                      focus:border-bronze focus:outline-none"
                  />
                </div>
                <button
                  onClick={() => removeParticipant(i)}
                  className="text-stone hover:text-terracotta"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
