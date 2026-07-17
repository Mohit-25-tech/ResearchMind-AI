import { FileText, BookOpen } from "lucide-react";
import type { Source } from "../../types/chat";

interface SourcePanelProps {
  sources: Source[];
}

export default function SourcePanel({ sources }: SourcePanelProps) {
  return (
    <aside className="flex flex-col h-full bg-surface">
      {/* Header */}
      <div className="px-3 pt-3 pb-2">
        <h2 className="text-[11px] font-semibold text-text-muted uppercase tracking-wider flex items-center gap-1.5">
          <BookOpen size={12} />
          Sources
        </h2>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto px-3 pb-3">
        {sources.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <FileText size={20} className="text-text-faint mb-2" />
            <p className="text-[11px] text-text-muted leading-relaxed">
              Sources will appear here
              <br />
              after you ask a question.
            </p>
          </div>
        ) : (
          <div className="flex flex-col gap-2">
            {sources.map((source, idx) => (
              <div
                key={`${source.document_id}-${idx}`}
                className="rounded-lg border border-border bg-surface-elevated/50 p-3"
              >
                {/* Filename */}
                <div className="flex items-start gap-1.5 mb-2">
                  <FileText size={12} className="text-accent mt-0.5 shrink-0" />
                  <p
                    className="text-xs font-medium text-text-primary truncate"
                    title={source.filename}
                  >
                    {source.filename}
                  </p>
                </div>

                {/* Page badges */}
                <div className="flex flex-wrap gap-1 mb-1.5">
                  {(Array.isArray(source.pages) ? source.pages : []).map((page) => (
                    <span
                      key={page}
                      className="inline-flex items-center px-1.5 py-0.5 rounded
                                 text-[10px] font-medium
                                 bg-accent-subtle text-accent"
                    >
                      p.{page + 1}
                    </span>
                  ))}
                </div>

                {/* Count */}
                <p className="text-[10px] text-text-muted">
                  {(Array.isArray(source.pages) ? source.pages.length : 0)}{" "}
                  {(Array.isArray(source.pages) ? source.pages.length : 0) === 1 ? "passage" : "passages"} retrieved
                </p>
              </div>
            ))}
          </div>
        )}
      </div>
    </aside>
  );
}
