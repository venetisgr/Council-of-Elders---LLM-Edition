import type { Provider } from "@/types";
import { getProviderColor } from "@/types/providers";

interface SpeakerLabelProps {
  speaker: string;
  provider: Provider;
}

export function SpeakerLabel({ speaker, provider }: SpeakerLabelProps) {
  const color = getProviderColor(provider);

  return (
    <div className="flex items-center gap-2">
      <div
        className="w-2.5 h-2.5 rounded-full flex-shrink-0"
        style={{ backgroundColor: color }}
      />
      <span
        className="text-sm font-semibold"
        style={{ color }}
      >
        {speaker}
      </span>
    </div>
  );
}
