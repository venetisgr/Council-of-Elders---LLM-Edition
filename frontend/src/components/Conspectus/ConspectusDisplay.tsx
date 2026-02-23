import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { FileText, Copy, Check, Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { MarkdownRenderer } from "@/components/common/MarkdownRenderer";
import { useDebateStore } from "@/stores/debateStore";

/** Split conspectus markdown into named sections keyed by heading. */
function parseSections(md: string): Map<string, string> {
  const sections = new Map<string, string>();
  const regex = /^## (.+)$/gm;
  const headings: { name: string; start: number }[] = [];
  let match: RegExpExecArray | null;
  while ((match = regex.exec(md)) !== null) {
    const captured = match[1];
    if (captured) {
      headings.push({ name: captured.trim().toLowerCase(), start: match.index });
    }
  }
  for (let i = 0; i < headings.length; i++) {
    const current = headings[i]!;
    const next = headings[i + 1];
    const end = next ? next.start : md.length;
    const body = md.slice(current.start, end).trim();
    sections.set(current.name, body);
  }
  return sections;
}

const OVERVIEW_KEY = "overview";
const SYNTHESIS_KEY = "synthesis";
const AGREEMENT_KEY = "points of agreement";
const DISAGREEMENT_KEY = "remaining disagreements";
const GROUPED_KEYS = new Set([OVERVIEW_KEY, SYNTHESIS_KEY, AGREEMENT_KEY, DISAGREEMENT_KEY]);

export function ConspectusDisplay() {
  const conspectus = useDebateStore((s) => s.conspectus);
  const generatingConspectus = useDebateStore((s) => s.generatingConspectus);
  const tokenUsage = useDebateStore((s) => s.tokenUsage);
  const currentRound = useDebateStore((s) => s.currentRound);
  const [copied, setCopied] = useState(false);
  const [showStats, setShowStats] = useState(false);

  const sections = useMemo(
    () => (conspectus ? parseSections(conspectus) : null),
    [conspectus],
  );

  if (!conspectus && !generatingConspectus) return null;

  const handleCopy = async () => {
    if (!conspectus) return;
    await navigator.clipboard.writeText(conspectus);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const totalTokens = Object.values(tokenUsage).reduce((a, b) => a + b, 0);

  // Collect remaining sections (everything not in the three main cards)
  const remaining: string[] = [];
  if (sections) {
    for (const [key, body] of sections) {
      if (!GROUPED_KEYS.has(key)) remaining.push(body);
    }
  }

  const hasParsedSections = sections && sections.size > 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="border-t border-stone/20 bg-marble"
    >
      <div className="px-4 py-3">
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
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

        {/* Loading */}
        {generatingConspectus && !conspectus && (
          <div className="flex items-center gap-2 py-4 text-sm text-stone">
            <Loader2 className="h-4 w-4 animate-spin text-bronze" />
            Generating conspectus...
          </div>
        )}

        {/* Sectioned layout */}
        {conspectus && hasParsedSections && (
          <div className="space-y-3">
            {/* Card 1: Overview */}
            {sections.has(OVERVIEW_KEY) && (
              <div className="rounded-lg border border-stone/15 bg-white/70 px-4 py-3 shadow-sm">
                <MarkdownRenderer content={sections.get(OVERVIEW_KEY)!} />
              </div>
            )}

            {/* Card 2: Synthesis + Agreements + Disagreements */}
            {(sections.has(SYNTHESIS_KEY) ||
              sections.has(AGREEMENT_KEY) ||
              sections.has(DISAGREEMENT_KEY)) && (
              <div className="rounded-lg border border-stone/15 bg-white/70 px-4 py-3 shadow-sm space-y-4">
                {sections.has(SYNTHESIS_KEY) && (
                  <MarkdownRenderer content={sections.get(SYNTHESIS_KEY)!} />
                )}
                {sections.has(AGREEMENT_KEY) && (
                  <MarkdownRenderer content={sections.get(AGREEMENT_KEY)!} />
                )}
                {sections.has(DISAGREEMENT_KEY) && (
                  <MarkdownRenderer content={sections.get(DISAGREEMENT_KEY)!} />
                )}
              </div>
            )}

            {/* Card 3: Remaining sections */}
            {remaining.length > 0 && (
              <div className="rounded-lg border border-stone/15 bg-white/70 px-4 py-3 shadow-sm space-y-4">
                {remaining.map((body, i) => (
                  <MarkdownRenderer key={i} content={body} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Fallback: render as single block if parsing found no headings */}
        {conspectus && !hasParsedSections && (
          <div className="rounded-lg border border-stone/15 bg-white/70 px-4 py-3 shadow-sm">
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
