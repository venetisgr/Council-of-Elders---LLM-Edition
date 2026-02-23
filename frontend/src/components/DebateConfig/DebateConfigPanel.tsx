import { MessageSquare, Swords } from "lucide-react";
import { ParticipantSelector } from "./ParticipantSelector";
import { ParameterControls } from "./ParameterControls";
import { Button } from "@/components/common/Button";
import { useConfigStore } from "@/stores/configStore";
import { useKeyStore } from "@/stores/keyStore";
import { useDebateStore } from "@/stores/debateStore";

export function DebateConfigPanel() {
  const {
    topic,
    setTopic,
    participants,
    maxRounds,
    maxTokensPerTurn,
    consensusThreshold,
    moderatorIndex,
    canStartDebate,
  } = useConfigStore();

  const { getApiKeys } = useKeyStore();
  const { startDebate } = useDebateStore();

  const handleStart = () => {
    if (!canStartDebate()) return;

    const apiKeys = getApiKeys();
    startDebate(
      {
        topic,
        participants,
        max_rounds: maxRounds,
        max_tokens_per_turn: maxTokensPerTurn,
        consensus_threshold: consensusThreshold,
        moderator_index: moderatorIndex,
      },
      apiKeys
    );
  };

  return (
    <div className="rounded-xl border border-stone/20 bg-white/80 backdrop-blur-sm p-6 shadow-sm">
      <div className="flex items-center gap-2 mb-4">
        <Swords className="h-5 w-5 text-bronze" />
        <h2 className="font-display text-lg text-ink">Debate Configuration</h2>
      </div>

      {/* Topic */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-2">
          <MessageSquare className="h-4 w-4 text-bronze" />
          <label className="text-sm font-semibold text-ink">
            Topic of Debate
          </label>
        </div>
        <textarea
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter the topic for the Council to deliberate upon..."
          rows={3}
          className="w-full rounded-lg border border-stone/30 bg-white px-3 py-2
            text-sm text-ink placeholder:text-stone/50
            focus:border-bronze focus:outline-none focus:ring-1 focus:ring-bronze/30
            resize-none"
        />
      </div>

      {/* Participants */}
      <div className="mb-6">
        <ParticipantSelector />
      </div>

      {/* Parameters */}
      <div className="mb-6">
        <ParameterControls />
      </div>

      {/* Start button */}
      <Button
        variant="primary"
        onClick={handleStart}
        disabled={!canStartDebate()}
        className="w-full py-3 text-base font-display"
      >
        <Swords className="h-5 w-5" />
        Begin Debate
      </Button>

      {!canStartDebate() && (
        <p className="mt-2 text-center text-xs text-stone">
          {!topic.trim()
            ? "Enter a topic to continue."
            : "Add at least 2 participants."}
        </p>
      )}
    </div>
  );
}
