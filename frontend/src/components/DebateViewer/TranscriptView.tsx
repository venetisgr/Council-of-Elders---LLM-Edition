import { useRef, useEffect, useState, useCallback } from "react";
import { MessageBubble } from "./MessageBubble";
import { useDebateStore } from "@/stores/debateStore";

export function TranscriptView() {
  const transcript = useDebateStore((s) => s.transcript);
  const currentRound = useDebateStore((s) => s.currentRound);
  const containerRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (autoScroll && containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [transcript, autoScroll]);

  const handleScroll = useCallback(() => {
    const el = containerRef.current;
    if (!el) return;
    // If user scrolls up more than 100px from bottom, disable auto-scroll
    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 100;
    setAutoScroll(atBottom);
  }, []);

  // Group messages by round
  let lastRound = 0;

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      className="flex-1 overflow-y-auto scroll-thin space-y-4 p-4"
    >
      {transcript.length === 0 && (
        <div className="flex items-center justify-center h-full text-stone/50 text-sm">
          The Council awaits...
        </div>
      )}

      {transcript.map((msg, i) => {
        const showRoundHeader = msg.round_number > lastRound;
        if (showRoundHeader) lastRound = msg.round_number;

        return (
          <div key={i}>
            {showRoundHeader && (
              <div className="flex items-center gap-3 my-4">
                <div className="flex-1 h-px bg-stone/20" />
                <span className="text-xs font-display text-stone uppercase tracking-wider">
                  Round {msg.round_number}
                  {msg.round_number === currentRound && " — In Progress"}
                </span>
                <div className="flex-1 h-px bg-stone/20" />
              </div>
            )}
            <MessageBubble message={msg} />
          </div>
        );
      })}

      {!autoScroll && transcript.length > 0 && (
        <button
          onClick={() => {
            setAutoScroll(true);
            containerRef.current?.scrollTo({
              top: containerRef.current.scrollHeight,
              behavior: "smooth",
            });
          }}
          className="sticky bottom-2 left-1/2 -translate-x-1/2
            rounded-full bg-bronze/90 text-white text-xs px-3 py-1.5
            shadow-md hover:bg-bronze"
        >
          Scroll to bottom
        </button>
      )}
    </div>
  );
}
