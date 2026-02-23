import { Settings } from "lucide-react";
import { Slider } from "@/components/common/Slider";
import { useConfigStore } from "@/stores/configStore";

export function ParameterControls() {
  const {
    maxRounds,
    maxTokensPerTurn,
    temperature,
    consensusThreshold,
    setMaxRounds,
    setMaxTokensPerTurn,
    setTemperature,
    setConsensusThreshold,
  } = useConfigStore();

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-2">
        <Settings className="h-4 w-4 text-bronze" />
        <h3 className="text-sm font-semibold text-ink">Parameters</h3>
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
          label="Temperature"
          value={temperature}
          min={0}
          max={2}
          step={0.1}
          onChange={setTemperature}
          formatValue={(v) => v.toFixed(1)}
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
      </div>
    </div>
  );
}
