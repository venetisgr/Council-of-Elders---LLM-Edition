import { Pause, Play, Square, RotateCcw } from "lucide-react";
import { Button } from "@/components/common/Button";
import { useDebateStore } from "@/stores/debateStore";
import { DebateStatus } from "@/types";

interface DebateControlsProps {
  onNewDebate: () => void;
}

const statusLabels: Record<string, string> = {
  idle: "Idle",
  pending: "Starting...",
  running: "In Progress",
  paused: "Paused",
  concluded: "Concluded",
  error: "Error",
};

const statusColors: Record<string, string> = {
  idle: "bg-stone/20 text-stone",
  pending: "bg-bronze/20 text-bronze",
  running: "bg-olive/20 text-olive",
  paused: "bg-bronze/20 text-bronze",
  concluded: "bg-ocean/20 text-ocean",
  error: "bg-terracotta/20 text-terracotta",
};

export function DebateControls({ onNewDebate }: DebateControlsProps) {
  const status = useDebateStore((s) => s.status);
  const currentRound = useDebateStore((s) => s.currentRound);
  const currentSpeaker = useDebateStore((s) => s.currentSpeaker);
  const { pauseDebate, resumeDebate, stopDebate } = useDebateStore();

  const isActive =
    status === DebateStatus.RUNNING || status === DebateStatus.PAUSED;
  const isConcluded = status === DebateStatus.CONCLUDED;

  return (
    <div className="flex items-center justify-between border-t border-stone/20 px-4 py-3 bg-sand/30">
      {/* Status badge and info */}
      <div className="flex items-center gap-3">
        <span
          className={`text-xs font-medium px-2.5 py-1 rounded-full ${statusColors[status] ?? statusColors.idle}`}
        >
          {statusLabels[status] ?? status}
        </span>
        {currentRound > 0 && (
          <span className="text-xs text-stone">Round {currentRound}</span>
        )}
        {currentSpeaker && (
          <span className="text-xs text-stone animate-pulse">
            {currentSpeaker} is speaking...
          </span>
        )}
      </div>

      {/* Controls */}
      <div className="flex items-center gap-2">
        {isActive && (
          <>
            {status === DebateStatus.RUNNING ? (
              <Button
                variant="secondary"
                onClick={pauseDebate}
                className="text-xs"
              >
                <Pause className="h-3.5 w-3.5" />
                Pause
              </Button>
            ) : (
              <Button
                variant="secondary"
                onClick={resumeDebate}
                className="text-xs"
              >
                <Play className="h-3.5 w-3.5" />
                Resume
              </Button>
            )}
            <Button
              variant="danger"
              onClick={stopDebate}
              className="text-xs"
            >
              <Square className="h-3.5 w-3.5" />
              Stop
            </Button>
          </>
        )}
        {(isConcluded || status === DebateStatus.ERROR) && (
          <Button variant="primary" onClick={onNewDebate} className="text-xs">
            <RotateCcw className="h-3.5 w-3.5" />
            New Debate
          </Button>
        )}
      </div>
    </div>
  );
}
