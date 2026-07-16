import { FileText, BookOpen } from "lucide-react";
import type { Source } from "../../types/chat";

interface SourcePanelProps {
  sources: Source[];
}

export default function SourcePanel({ sources }: SourcePanelProps) {
  return (
    <aside className="flex flex-col h-full border-l border-border bg-surface">
      {/* Header */}
      <div className="px-4 py-3.5 border-b border-border">
        <h2 className="text-sm font-semibold text-text-primary flex items-center gap-2">
          <BookOpen size={15} className="text-text-secondary" />
          Sources
        </h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-4 py-3">
        {sources.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <FileText size={28} className="text-text-muted mb-3" />
            <p className="text-xs text-text-muted leading-relaxed">
              Sources will appear here<br />after you ask a question.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-3">
            {sources.map((source, idx) => (
              <div
                key={`${source.document_id}-${idx}`}
                className="rounded-xl border border-border bg-surface-elevated p-3.5"
              >
                {/* Filename */}
                <div className="flex items-start gap-2 mb-2.5">
                  <FileText
                    size={14}
                    className="text-accent mt-0.5 shrink-0"
                  />
                  <p
                    className="text-sm font-medium text-text-primary truncate"
                    title={source.filename}
                  >
                    {source.filename}
                  </p>
                </div>

                {/* Page badges */}
                <div className="flex flex-wrap gap-1.5 mb-2">
                  {source.pages.map((page) => (
                    <span
                      key={page}
                      className="inline-flex items-center px-2 py-0.5 rounded-md
                                 text-[11px] font-medium
                                 bg-accent-subtle text-accent"
                    >
                      p.{page + 1}
                    </span>
                  ))}
                </div>

                {/* Passages count */}
                <p className="text-[11px] text-text-muted">
                  {source.pages.length} {source.pages.length === 1 ? "passage" : "passages"} retrieved
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}
