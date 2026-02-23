import { ApiKeyPanel } from "@/components/ApiKeyPanel/ApiKeyPanel";
import { DebateConfigPanel } from "@/components/DebateConfig/DebateConfigPanel";
import { DebateViewer } from "@/components/DebateViewer/DebateViewer";
import { ToastProvider } from "@/components/common/Toast";
import { useDebateStore } from "@/stores/debateStore";
import { useConfigStore } from "@/stores/configStore";
import { DebateStatus } from "@/types";
import { Landmark } from "lucide-react";

function AppContent() {
  const status = useDebateStore((s) => s.status);
  const resetDebate = useDebateStore((s) => s.reset);
  const resetConfig = useConfigStore((s) => s.reset);

  const isSetupPhase = status === DebateStatus.IDLE;

  const handleNewDebate = () => {
    resetDebate();
    resetConfig();
  };

  return (
    <div className="min-h-screen bg-marble">
      {/* Header */}
      <header className="border-b border-stone/20 bg-white/60 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center gap-3">
          <Landmark className="h-7 w-7 text-bronze" />
          <div>
            <h1 className="font-display text-xl text-ink leading-tight">
              Council of Elders
            </h1>
            <p className="text-xs text-stone">LLM Edition</p>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {isSetupPhase ? (
          /* Setup phase: API keys + config side by side */
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ApiKeyPanel />
            <DebateConfigPanel />
          </div>
        ) : (
          /* Debate phase: full-width viewer */
          <div className="rounded-xl border border-stone/20 bg-white/80 backdrop-blur-sm shadow-sm overflow-hidden min-h-[600px] flex flex-col">
            <DebateViewer onNewDebate={handleNewDebate} />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-stone/10 py-4 mt-8">
        <p className="text-center text-xs text-stone/50">
          Council of Elders — Where LLMs deliberate in the spirit of the
          Athenian Agora
        </p>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <ToastProvider>
      <AppContent />
    </ToastProvider>
  );
}
