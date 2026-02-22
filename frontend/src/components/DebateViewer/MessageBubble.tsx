import { SpeakerLabel } from "./SpeakerLabel";
import { MarkdownRenderer } from "@/components/common/MarkdownRenderer";
import type { DebateMessage } from "@/types";
import { getProviderColor } from "@/types/providers";

interface MessageBubbleProps {
  message: DebateMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const color = getProviderColor(message.provider);

  return (
    <div className="group">
      <div className="flex items-center gap-2 mb-1">
        <SpeakerLabel speaker={message.speaker} provider={message.provider} />
        <span className="text-xs text-stone">Round {message.round_number}</span>
        {message.token_count > 0 && (
          <span className="text-xs text-stone/60 opacity-0 group-hover:opacity-100 transition-opacity">
            {message.token_count} tokens
          </span>
        )}
      </div>

      <div
        className="ml-5 rounded-lg border px-4 py-3 bg-white/60"
        style={{ borderColor: `${color}20` }}
      >
        {message.content ? (
          <div className={message.isStreaming ? "streaming-cursor" : ""}>
            <MarkdownRenderer content={message.content} />
          </div>
        ) : message.isStreaming ? (
          <div className="flex items-center gap-1.5 py-1">
            <div
              className="w-2 h-2 rounded-full animate-bounce"
              style={{ backgroundColor: color, animationDelay: "0ms" }}
            />
            <div
              className="w-2 h-2 rounded-full animate-bounce"
              style={{ backgroundColor: color, animationDelay: "150ms" }}
            />
            <div
              className="w-2 h-2 rounded-full animate-bounce"
              style={{ backgroundColor: color, animationDelay: "300ms" }}
            />
          </div>
        ) : null}
      </div>
    </div>
  );
}
