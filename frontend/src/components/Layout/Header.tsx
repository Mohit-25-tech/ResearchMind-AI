import { BrainCircuit } from "lucide-react";

export default function Header() {
  return (
    <header
      className="flex items-center gap-3 px-6 py-3.5 border-b border-border bg-surface"
    >
      <div className="flex items-center gap-2.5">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-accent-subtle">
          <BrainCircuit size={18} className="text-accent" />
        </div>
        <h1 className="text-base font-semibold tracking-tight text-text-primary">
          AI Research Assistant
        </h1>
      </div>
      <div className="ml-auto flex items-center gap-2">
        <span className="text-xs text-text-muted px-2 py-1 rounded-md bg-surface-elevated">
          v1.0
        </span>
      </div>
    </header>
  );
}
