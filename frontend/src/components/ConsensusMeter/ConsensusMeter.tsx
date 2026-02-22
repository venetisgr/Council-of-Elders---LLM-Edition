import { useState } from "react";
import { motion } from "framer-motion";
import { ChevronDown, ChevronUp } from "lucide-react";
import { useDebateStore } from "@/stores/debateStore";

function getBarColor(score: number): string {
  if (score < 0.3) return "#CC5533"; // terracotta
  if (score < 0.6) return "#D4AF37"; // gold
  return "#556B2F"; // olive
}

export function ConsensusMeter() {
  const consensusHistory = useDebateStore((s) => s.consensusHistory);
  const [expanded, setExpanded] = useState(false);

  const latest = consensusHistory[consensusHistory.length - 1];
  if (!latest) {
    return (
      <div className="border-b border-stone/20 px-4 py-2 bg-sand/20">
        <div className="flex items-center justify-between">
          <span className="text-xs text-stone">Consensus</span>
          <span className="text-xs text-stone/50">Awaiting first round...</span>
        </div>
        <div className="mt-1.5 h-2 rounded-full bg-stone/10 overflow-hidden">
          <div className="h-full w-0 rounded-full bg-stone/20" />
        </div>
      </div>
    );
  }

  const score = latest.consensus_score;
  const pct = Math.round(score * 100);
  const color = getBarColor(score);

  return (
    <div className="border-b border-stone/20 px-4 py-2 bg-sand/20">
      <div className="flex items-center justify-between">
        <span className="text-xs text-stone">Consensus</span>
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold" style={{ color }}>
            {pct}%
          </span>
          {latest.stagnation_detected && (
            <span className="text-xs bg-bronze/10 text-bronze px-1.5 py-0.5 rounded">
              Stagnation
            </span>
          )}
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-stone hover:text-ink"
          >
            {expanded ? (
              <ChevronUp className="h-3.5 w-3.5" />
            ) : (
              <ChevronDown className="h-3.5 w-3.5" />
            )}
          </button>
        </div>
      </div>

      {/* Animated bar */}
      <div className="mt-1.5 h-2 rounded-full bg-stone/10 overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </div>

      {/* Expanded details */}
      {expanded && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          exit={{ opacity: 0, height: 0 }}
          className="mt-3 space-y-2"
        >
          {latest.summary && (
            <p className="text-xs text-stone">{latest.summary}</p>
          )}

          {latest.agreed_points.length > 0 && (
            <div>
              <span className="text-xs font-medium text-olive">
                Agreed Points:
              </span>
              <ul className="mt-1 space-y-0.5">
                {latest.agreed_points.map((point, i) => (
                  <li key={i} className="text-xs text-ink/80 pl-3 relative">
                    <span className="absolute left-0 text-olive">+</span>
                    {point}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {latest.contested_points.length > 0 && (
            <div>
              <span className="text-xs font-medium text-terracotta">
                Contested Points:
              </span>
              <ul className="mt-1 space-y-0.5">
                {latest.contested_points.map((point, i) => (
                  <li key={i} className="text-xs text-ink/80 pl-3 relative">
                    <span className="absolute left-0 text-terracotta">-</span>
                    {point}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* History mini-chart */}
          {consensusHistory.length > 1 && (
            <div className="flex items-end gap-1 h-8 pt-2">
              {consensusHistory.map((c, i) => (
                <div
                  key={i}
                  className="flex-1 rounded-t"
                  style={{
                    height: `${Math.max(c.consensus_score * 100, 5)}%`,
                    backgroundColor: getBarColor(c.consensus_score),
                    opacity: i === consensusHistory.length - 1 ? 1 : 0.5,
                  }}
                  title={`Round ${c.round}: ${Math.round(c.consensus_score * 100)}%`}
                />
              ))}
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}
