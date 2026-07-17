import { BrainCircuit } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface HeaderProps {
  selectedDocumentName: string | null;
}

export default function Header({ selectedDocumentName }: HeaderProps) {
  const navigate = useNavigate();

  return (
    <header className="flex items-center gap-3 px-4 h-12 border-b border-border bg-surface/80 backdrop-blur-sm shrink-0">
      <button
        onClick={() => navigate("/")}
        className="flex items-center gap-2 cursor-pointer hover:opacity-80 transition-opacity"
      >
        <div className="flex items-center justify-center w-6 h-6 rounded-md bg-accent-subtle">
          <BrainCircuit size={13} className="text-accent" />
        </div>
        <span className="text-[13px] font-semibold tracking-tight text-text-primary">
          ResearchMind
        </span>
      </button>

      {/* Separator */}
      <div className="w-px h-4 bg-border" />

      {/* Context indicator */}
      <span className="text-xs text-text-muted truncate">
        {selectedDocumentName ? (
          <>
            Chatting with{" "}
            <span className="text-text-secondary font-medium">{selectedDocumentName}</span>
          </>
        ) : (
          "All Documents"
        )}
      </span>

      <div className="ml-auto">
        <span className="text-[10px] text-text-faint px-1.5 py-0.5 rounded bg-surface-elevated">
          v1.0
        </span>
      </div>
    </header>
  );
}
