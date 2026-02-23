import { useState } from "react";
import { ChevronDown, ChevronUp, BookOpen } from "lucide-react";

export function HowItWorks() {
  const [open, setOpen] = useState(false);

  return (
    <section className="max-w-7xl mx-auto px-4 mt-8">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-center gap-2 text-sm font-medium text-bronze hover:text-ink transition-colors py-2"
      >
        <BookOpen className="h-4 w-4" />
        How the Agora Works
        {open ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
      </button>

      {open && (
        <div className="rounded-xl border border-stone/20 bg-white/80 backdrop-blur-sm p-6 shadow-sm mt-2 mb-4 text-sm text-ink leading-relaxed space-y-6">

          {/* ---- Overview ---- */}
          <div>
            <h3 className="font-display text-base font-semibold mb-2">What is the Ancient Athenian Agora?</h3>
            <p>
              The <strong>Ancient Athenian Agora</strong> is a first-of-its-kind platform that brings the
              world's leading AI models together for structured, multi-round deliberation on any topic you
              choose. Instead of asking one model and hoping for the best, pit Claude, GPT, Gemini, Grok,
              DeepSeek, Kimi, Qwen, and GLM against each other in a live debate — and let them argue,
              challenge, and refine each other's reasoning in real time.
            </p>
            <p className="mt-2">
              Think of it as a <strong>virtual panel of AI experts</strong>. Each participant brings a
              different training background, knowledge base, and reasoning style. By forcing them to
              engage directly with each other's arguments — agreeing where they find common ground and
              pushing back where they don't — the Agora surfaces insights, blind spots, and nuances
              that no single model would produce alone.
            </p>
            <p className="mt-3 font-semibold">Use it to:</p>
            <ul className="mt-1 list-disc list-inside text-stone space-y-1">
              <li><strong>Stress-test an idea</strong> — Get diverse AI perspectives before committing to a strategy, architecture, or decision.</li>
              <li><strong>Research complex topics</strong> — Let multiple models debate the evidence and trade-offs so you see the full picture.</li>
              <li><strong>Evaluate AI reasoning</strong> — Compare how different models approach the same problem, where they agree, and where they diverge.</li>
              <li><strong>Generate robust conclusions</strong> — The consensus engine and final conspectus distill hours of potential research into a structured, multi-perspective summary.</li>
              <li><strong>Learn and explore</strong> — Pose philosophical, scientific, or creative questions and watch genuinely different viewpoints collide.</li>
            </ul>
            <p className="mt-3">
              Your API keys never leave your browser session and are never stored on any server. You bring
              your own keys, you own the conversation, and you control every parameter — from per-participant
              temperature and persona to the consensus threshold and moderator selection.
            </p>
          </div>

          {/* ---- Debate Flow ---- */}
          <div>
            <h3 className="font-display text-base font-semibold mb-2">Debate Flow</h3>
            <p>
              A debate proceeds in <strong>rounds</strong>. In each round every participant speaks
              exactly once in the order they were added (round-robin). Each participant receives the
              full transcript of everything said so far, plus a system prompt that establishes their
              identity, persona (if assigned), and the rules of the Agora. They are instructed to
              engage directly with other speakers' arguments, agree explicitly when they find common
              ground, and disagree with precision when they don't.
            </p>
            <p className="mt-2">
              After all participants have spoken in a round, a <strong>consensus check</strong> is
              performed. If the composite consensus score meets or exceeds the configured threshold,
              the debate ends. Otherwise the next round begins. The debate also terminates when the
              maximum number of rounds is reached or when stagnation is detected for three
              consecutive rounds.
            </p>
          </div>

          {/* ---- Consensus Score ---- */}
          <div>
            <h3 className="font-display text-base font-semibold mb-2">Consensus Score (0.0 – 1.0)</h3>
            <p>
              The consensus score is a <strong>weighted composite</strong> of three independent
              signals, computed after every round:
            </p>

            <div className="mt-3 space-y-4">
              {/* Signal 1 */}
              <div className="pl-4 border-l-2 border-bronze/30">
                <p className="font-semibold">Signal 1 — Agreement Markers <span className="font-normal text-stone">(weight: 25%)</span></p>
                <p className="mt-1">
                  A text-scanning heuristic that counts how often participants use explicit
                  agreement phrases versus disagreement phrases in their responses.
                </p>
                <div className="mt-2 grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  <div className="rounded bg-olive/10 px-3 py-2">
                    <p className="font-semibold text-olive mb-1">Agreement phrases</p>
                    <p className="text-stone">"i agree", "i concur", "that's correct", "building on",
                      "exactly right", "well said", "i share", "common ground",
                      "we seem to converge", "as [name] correctly pointed out",
                      "aligns with my view", "i must acknowledge"</p>
                  </div>
                  <div className="rounded bg-terracotta/10 px-3 py-2">
                    <p className="font-semibold text-terracotta mb-1">Disagreement phrases</p>
                    <p className="text-stone">"i disagree", "i must counter", "however",
                      "on the contrary", "that misses", "i take issue",
                      "fundamentally flawed", "i challenge", "that overlooks", "insufficient"</p>
                  </div>
                </div>
                <p className="mt-2 text-xs text-stone">
                  Formula: <code className="bg-sand/50 px-1 rounded">agreement_count / (agreement_count + disagreement_count)</code>.
                  If no markers are found at all, the score defaults to 0.5 (neutral).
                </p>
              </div>

              {/* Signal 2 */}
              <div className="pl-4 border-l-2 border-bronze/30">
                <p className="font-semibold">Signal 2 — LLM Moderator Analysis <span className="font-normal text-stone">(weight: 60%)</span></p>
                <p className="mt-1">
                  The participant you select as <strong>Moderator</strong> in the Argument Parameters
                  also acts as an impartial judge. After each round, the moderator LLM receives the
                  round's transcript and is prompted as an "impartial observer at the Agora" to
                  return a structured JSON assessment containing:
                </p>
                <ul className="mt-1 list-disc list-inside text-stone">
                  <li><strong>consensus_score</strong> — a 0.0 to 1.0 rating of how much the speakers agree</li>
                  <li><strong>agreed_points</strong> — specific points where speakers converge</li>
                  <li><strong>contested_points</strong> — specific points where they diverge</li>
                  <li><strong>stagnation</strong> — whether arguments are repetitive and not advancing</li>
                  <li><strong>summary</strong> — a one-sentence assessment of the debate's current state</li>
                </ul>
                <p className="mt-2 text-xs text-stone">
                  This call uses a low temperature (0.1) and a 512-token limit for deterministic,
                  concise analysis. If the call fails for any reason, the LLM score defaults to 0.5.
                </p>
              </div>

              {/* Signal 3 */}
              <div className="pl-4 border-l-2 border-bronze/30">
                <p className="font-semibold">Signal 3 — Stagnation Detection <span className="font-normal text-stone">(weight: 15%)</span></p>
                <p className="mt-1">
                  Detects whether the debate is going in circles by comparing the vocabulary of the
                  current round to the previous round. All responses in each round are lowercased and
                  split into word sets, then the overlap ratio is computed:
                </p>
                <p className="mt-2 text-xs text-stone">
                  Formula: <code className="bg-sand/50 px-1 rounded">|current_words &cap; previous_words| / |current_words &cup; previous_words|</code>
                </p>
                <p className="mt-1">
                  If more than <strong>80%</strong> of the words overlap between rounds, stagnation is
                  flagged. When stagnation is detected, a penalty of 0.3 is applied (the signal
                  contributes 0.105 instead of 0.15). Stagnation cannot be detected in the first round
                  since there is no prior round to compare against.
                </p>
              </div>
            </div>

            {/* Final formula */}
            <div className="mt-4 rounded-lg bg-sand/40 px-4 py-3">
              <p className="font-semibold mb-1">Final Composite Formula</p>
              <code className="text-xs block bg-white/60 rounded px-3 py-2">
                consensus = 0.25 &times; marker_score + 0.60 &times; llm_score + 0.15 &times; (1.0 &minus; stagnation_penalty)
              </code>
              <p className="mt-2 text-xs text-stone">
                The result is clamped to [0.0, 1.0]. When there is no stagnation the third term
                contributes a full 0.15; when stagnation is detected the penalty (0.3) reduces it
                to 0.105, lowering the composite by 0.045.
              </p>
            </div>
          </div>

          {/* ---- Consensus Threshold ---- */}
          <div>
            <h3 className="font-display text-base font-semibold mb-2">Consensus Threshold</h3>
            <p>
              The threshold (default 80%, configurable from 0% to 100%) is the target composite
              score that ends the debate. After every round, if{" "}
              <code className="bg-sand/50 px-1 rounded text-xs">consensus_score &ge; threshold</code>,
              the debate concludes with "consensus reached". A lower threshold means the debate ends
              sooner (participants don't need to agree as strongly); a higher threshold demands near-total
              alignment before the debate will stop on its own.
            </p>
            <p className="mt-2">
              Even if the threshold is never reached, the debate still terminates when:
            </p>
            <ul className="mt-1 list-disc list-inside text-stone">
              <li>The maximum number of rounds is exhausted.</li>
              <li>Stagnation is detected for <strong>3 consecutive rounds</strong>, indicating the
                participants are repeating themselves and further rounds are unlikely to produce
                new insight.</li>
            </ul>
          </div>

          {/* ---- Termination & Conspectus ---- */}
          <div>
            <h3 className="font-display text-base font-semibold mb-2">Conspectus (Final Summary)</h3>
            <p>
              When the debate concludes — whether by consensus, stagnation, max rounds, or manual
              stop — the moderator LLM generates a <strong>conspectus</strong>: a structured summary
              of the entire deliberation. It receives the full transcript, participant names, round
              count, and final consensus score, and produces five sections: Overview, Key Arguments,
              Points of Agreement, Remaining Disagreements, and Synthesis.
            </p>
          </div>

          {/* ---- Configuration ---- */}
          <div>
            <h3 className="font-display text-base font-semibold mb-2">Configuration Reference</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-xs border-collapse">
                <thead>
                  <tr className="border-b border-stone/20 text-left">
                    <th className="py-2 pr-4 font-semibold">Setting</th>
                    <th className="py-2 pr-4 font-semibold">Default</th>
                    <th className="py-2 font-semibold">Description</th>
                  </tr>
                </thead>
                <tbody className="text-stone">
                  <tr className="border-b border-stone/10">
                    <td className="py-2 pr-4 font-medium text-ink">Temperature</td>
                    <td className="py-2 pr-4">0.45</td>
                    <td className="py-2">Per-participant. Controls randomness of each LLM's responses. Higher values (up to 2.0) produce more creative, varied output; lower values produce more focused, deterministic responses.</td>
                  </tr>
                  <tr className="border-b border-stone/10">
                    <td className="py-2 pr-4 font-medium text-ink">Persona</td>
                    <td className="py-2 pr-4">None</td>
                    <td className="py-2">Per-participant. An optional perspective (e.g. "pragmatist", "skeptic") injected into the LLM's system prompt as "Your assigned perspective: ...".</td>
                  </tr>
                  <tr className="border-b border-stone/10">
                    <td className="py-2 pr-4 font-medium text-ink">Max Rounds</td>
                    <td className="py-2 pr-4">10</td>
                    <td className="py-2">Upper limit on debate rounds (1–50). The debate ends after this many rounds even if no consensus is reached.</td>
                  </tr>
                  <tr className="border-b border-stone/10">
                    <td className="py-2 pr-4 font-medium text-ink">Max Tokens / Turn</td>
                    <td className="py-2 pr-4">1024</td>
                    <td className="py-2">Maximum tokens each participant can produce per turn (100–4096). Controls response length.</td>
                  </tr>
                  <tr className="border-b border-stone/10">
                    <td className="py-2 pr-4 font-medium text-ink">Consensus Threshold</td>
                    <td className="py-2 pr-4">80%</td>
                    <td className="py-2">The composite consensus score required to end the debate (0%–100%).</td>
                  </tr>
                  <tr>
                    <td className="py-2 pr-4 font-medium text-ink">Moderator</td>
                    <td className="py-2 pr-4">First participant</td>
                    <td className="py-2">The participant whose LLM evaluates consensus after each round and writes the final conspectus.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

        </div>
      )}
    </section>
  );
}
