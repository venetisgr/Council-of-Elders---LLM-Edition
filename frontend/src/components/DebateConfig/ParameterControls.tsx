import { Settings } from "lucide-react";
import { Slider } from "@/components/common/Slider";
import { useConfigStore } from "@/stores/configStore";

export function ParameterControls() {
  const {
    participants,
    maxRounds,
    maxTokensPerTurn,
    consensusThreshold,
    moderatorIndex,
    setMaxRounds,
    setMaxTokensPerTurn,
    setConsensusThreshold,
    setModeratorIndex,
  } = useConfigStore();

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-2">
        <Settings className="h-4 w-4 text-bronze" />
        <h3 className="text-sm font-semibold text-ink">Argument Parameters</h3>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Slider
          label="Max Rounds"
          value={maxRounds}
          min={1}
          max={50}
          step={1}
          onChange={setMaxRounds}
        />
        <Slider
          label="Max Tokens / Turn"
          value={maxTokensPerTurn}
          min={100}
          max={4096}
          step={100}
          onChange={setMaxTokensPerTurn}
        />
        <Slider
          label="Consensus Threshold"
          value={consensusThreshold}
          min={0}
          max={1}
          step={0.05}
          onChange={setConsensusThreshold}
          formatValue={(v) => `${Math.round(v * 100)}%`}
        />

        {/* Moderator selector */}
        <div className="space-y-1">
          <label className="text-xs font-medium text-ink">Moderator</label>
          <select
            value={moderatorIndex}
            onChange={(e) => setModeratorIndex(Number(e.target.value))}
            className="w-full rounded-lg border border-stone/30 bg-white px-3 py-2
              text-sm text-ink focus:border-bronze focus:outline-none"
          >
            {participants.length === 0 ? (
              <option value={0}>Add participants first</option>
            ) : (
              participants.map((p, i) => (
                <option key={i} value={i}>
                  {p.display_name}
                </option>
              ))
            )}
          </select>
          <p className="text-[10px] text-stone">
            Evaluates consensus and writes the final conspectus
          </p>
        </div>
      </div>
    </div>
  );
}
