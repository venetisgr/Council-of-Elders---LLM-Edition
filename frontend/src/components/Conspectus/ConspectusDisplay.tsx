import { useState } from "react";
import { motion } from "framer-motion";
import { FileText, Copy, Check, Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { MarkdownRenderer } from "@/components/common/MarkdownRenderer";
import { useDebateStore } from "@/stores/debateStore";

export function ConspectusDisplay() {
  const conspectus = useDebateStore((s) => s.conspectus);
  const generatingConspectus = useDebateStore((s) => s.generatingConspectus);
  const tokenUsage = useDebateStore((s) => s.tokenUsage);
  const currentRound = useDebateStore((s) => s.currentRound);
  const [copied, setCopied] = useState(false);
  const [showStats, setShowStats] = useState(false);

  if (!conspectus && !generatingConspectus) return null;

  const handleCopy = async () => {
    if (!conspectus) return;
    await navigator.clipboard.writeText(conspectus);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const totalTokens = Object.values(tokenUsage).reduce((a, b) => a + b, 0);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="border-t border-stone/20 bg-marble"
    >
      <div className="px-4 py-3">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4 text-gold" />
            <h3 className="font-display text-sm text-ink">Conspectus</h3>
          </div>
          <div className="flex items-center gap-2">
            {conspectus && (
              <button
                onClick={handleCopy}
                className="flex items-center gap-1 text-xs text-stone hover:text-ink"
              >
                {copied ? (
                  <Check className="h-3.5 w-3.5 text-olive" />
                ) : (
                  <Copy className="h-3.5 w-3.5" />
                )}
                {copied ? "Copied" : "Copy"}
              </button>
            )}
            <button
              onClick={() => setShowStats(!showStats)}
              className="text-stone hover:text-ink"
            >
              {showStats ? (
                <ChevronUp className="h-3.5 w-3.5" />
              ) : (
                <ChevronDown className="h-3.5 w-3.5" />
              )}
            </button>
          </div>
        </div>

        {generatingConspectus && !conspectus && (
          <div className="flex items-center gap-2 py-4 text-sm text-stone">
            <Loader2 className="h-4 w-4 animate-spin text-bronze" />
            Generating conspectus...
          </div>
        )}

        {conspectus && (
          <div className="max-h-64 overflow-y-auto scroll-thin">
            <MarkdownRenderer content={conspectus} />
          </div>
        )}

        {/* Stats */}
        {showStats && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            className="mt-3 pt-3 border-t border-stone/10"
          >
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs">
              <div className="rounded-lg bg-sand/50 px-3 py-2">
                <span className="text-stone">Total Rounds</span>
                <p className="font-semibold text-ink">{currentRound}</p>
              </div>
              <div className="rounded-lg bg-sand/50 px-3 py-2">
                <span className="text-stone">Total Tokens</span>
                <p className="font-semibold text-ink">
                  {totalTokens.toLocaleString()}
                </p>
              </div>
              {Object.entries(tokenUsage).map(([speaker, tokens]) => (
                <div key={speaker} className="rounded-lg bg-sand/50 px-3 py-2">
                  <span className="text-stone truncate block">{speaker}</span>
                  <p className="font-semibold text-ink">
                    {tokens.toLocaleString()} tokens
                  </p>
                </div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
