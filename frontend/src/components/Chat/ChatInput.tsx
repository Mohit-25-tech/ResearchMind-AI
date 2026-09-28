import { useRef, useEffect, useCallback } from "react";
import { ArrowUp, X, Layers } from "lucide-react";

export interface ScopedDocument {
  id: string;
  name: string;
}

interface ChatInputProps {
  isLoading: boolean;
  scopedDocuments?: ScopedDocument[];
  selectedDocumentName?: string | null;
  onRemoveScopedDocument?: (id: string) => void;
  onClearScope?: () => void;
  onSend: (message: string) => void;
}

export default function ChatInput({
  isLoading,
  scopedDocuments = [],
  selectedDocumentName = null,
  onRemoveScopedDocument,
  onClearScope,
  onSend,
}: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // If scopedDocuments is empty but legacy selectedDocumentName is provided
  const activeDocs: ScopedDocument[] =
    scopedDocuments.length > 0
      ? scopedDocuments
      : selectedDocumentName
      ? [{ id: "active-doc", name: selectedDocumentName }]
      : [];

  const placeholder =
    activeDocs.length === 1
      ? `Ask about "${activeDocs[0].name}"...`
      : activeDocs.length > 1
      ? `Ask across ${activeDocs.length} scoped documents...`
      : "Ask a question about your research papers...";

  const autoResize = useCallback(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 150)}px`;
  }, []);

  useEffect(() => {
    if (!isLoading && textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [isLoading]);

  function handleSend() {
    const text = textareaRef.current?.value.trim();
    if (!text || isLoading) return;
    onSend(text);
    if (textareaRef.current) {
      textareaRef.current.value = "";
      textareaRef.current.style.height = "auto";
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="border-t border-border bg-bg px-4 py-3">
      {/* Scoped Documents Pill Row */}
      {activeDocs.length > 0 && (
        <div className="max-w-3xl mx-auto mb-2 flex items-center flex-wrap gap-1.5 text-xs">
          <span className="text-text-muted text-[11px] font-medium flex items-center gap-1 mr-0.5">
            <Layers size={12} className="text-accent" />
            Scoped to:
          </span>
          {activeDocs.map((doc) => (
            <span
              key={doc.id}
              className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-accent-subtle border border-accent/20 text-accent text-[11px] font-medium max-w-[240px]"
              title={doc.name}
            >
              <span className="truncate">{doc.name}</span>
              {onRemoveScopedDocument && (
                <button
                  type="button"
                  onClick={() => onRemoveScopedDocument(doc.id)}
                  className="hover:text-accent-hover hover:bg-accent/10 rounded-full p-0.5 transition-colors cursor-pointer"
                  title={`Remove ${doc.name} from scope`}
                >
                  <X size={10} />
                </button>
              )}
            </span>
          ))}
          {onClearScope && (
            <button
              type="button"
              onClick={onClearScope}
              className="text-[11px] text-text-muted hover:text-text-secondary underline underline-offset-2 ml-1 cursor-pointer transition-colors"
            >
              Clear scope
            </button>
          )}
        </div>
      )}

      <div className="max-w-3xl mx-auto relative">
        <textarea
          ref={textareaRef}
          placeholder={placeholder}
          disabled={isLoading}
          onInput={autoResize}
          onKeyDown={handleKeyDown}
          rows={1}
          className="w-full resize-none rounded-xl bg-surface-elevated border border-border
                     pl-4 pr-12 py-3 text-sm text-text-primary placeholder:text-text-muted
                     focus:outline-none focus:border-accent/40 focus:ring-1 focus:ring-accent/10
                     disabled:opacity-40 disabled:cursor-not-allowed
                     transition-colors"
        />
        <button
          onClick={handleSend}
          disabled={isLoading}
          className="absolute right-2 bottom-2 flex items-center justify-center w-8 h-8 rounded-lg
                     bg-accent text-white hover:bg-accent-hover
                     disabled:opacity-30 disabled:cursor-not-allowed
                     transition-colors cursor-pointer"
          title="Send"
        >
          <ArrowUp size={15} />
        </button>
      </div>
      <p className="text-[10px] text-text-faint text-center mt-1.5">
        Enter to send · Shift+Enter for new line
      </p>
    </div>
  );
}
