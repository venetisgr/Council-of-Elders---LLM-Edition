import { TranscriptView } from "./TranscriptView";
import { DebateControls } from "./DebateControls";
import { ConsensusMeter } from "@/components/ConsensusMeter/ConsensusMeter";
import { ConspectusDisplay } from "@/components/Conspectus/ConspectusDisplay";
import { useDebateStore } from "@/stores/debateStore";
import { useConfigStore } from "@/stores/configStore";
import { DebateStatus } from "@/types";
import { AlertCircle } from "lucide-react";

interface DebateViewerProps {
  onNewDebate: () => void;
}

export function DebateViewer({ onNewDebate }: DebateViewerProps) {
  const status = useDebateStore((s) => s.status);
  const error = useDebateStore((s) => s.error);
  const topic = useConfigStore((s) => s.topic);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-stone/20 px-4 py-3 bg-white/60">
        <h2 className="font-display text-lg text-ink">The Agora</h2>
        <p className="text-sm text-bronze font-medium mt-0.5">
          TODAY'S DEBATE:{" "}
          <span className="text-ink">{topic}</span>
        </p>
      </div>

      {/* Error banner */}
      {error && (
        <div className="flex items-center gap-2 bg-terracotta/10 border-b border-terracotta/20 px-4 py-2">
          <AlertCircle className="h-4 w-4 text-terracotta flex-shrink-0" />
          <span className="text-sm text-terracotta">{error}</span>
        </div>
      )}

      {/* Consensus meter (shown during and after debate) */}
      {status !== DebateStatus.IDLE && status !== DebateStatus.PENDING && (
        <ConsensusMeter />
      )}

      {/* Transcript */}
      <TranscriptView />

      {/* Conspectus (shown when available) */}
      <ConspectusDisplay />

      {/* Controls */}
      <DebateControls onNewDebate={onNewDebate} />
    </div>
  );
}
