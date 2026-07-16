import { useRef, useEffect, useCallback } from "react";
import { SendHorizontal } from "lucide-react";

interface ChatInputProps {
  isLoading: boolean;
  selectedDocumentName: string | null;
  onSend: (message: string) => void;
}

export default function ChatInput({
  isLoading,
  selectedDocumentName,
  onSend,
}: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const placeholder = selectedDocumentName
    ? `Ask about "${selectedDocumentName}"...`
    : "Ask a question about your research papers...";

  // Auto-resize the textarea to fit content
  const autoResize = useCallback(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, []);

  // Reset height when loading finishes (message was sent)
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
    // Enter or Ctrl+Enter → send
    // Shift+Enter → newline
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="border-t border-border bg-surface px-4 py-3">
      <div className="flex items-end gap-2 max-w-4xl mx-auto">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            placeholder={placeholder}
            disabled={isLoading}
            onInput={autoResize}
            onKeyDown={handleKeyDown}
            rows={1}
            className="w-full resize-none rounded-xl bg-surface-elevated border border-border
                       px-4 py-3 text-sm text-text-primary placeholder:text-text-muted
                       focus:outline-none focus:border-accent/50 focus:ring-1 focus:ring-accent/20
                       disabled:opacity-50 disabled:cursor-not-allowed
                       transition-colors"
          />
        </div>
        <button
          onClick={handleSend}
          disabled={isLoading}
          className="flex items-center justify-center w-10 h-10 rounded-xl
                     bg-accent text-white hover:bg-accent-hover
                     disabled:opacity-40 disabled:cursor-not-allowed
                     transition-colors cursor-pointer shrink-0"
          title="Send message"
        >
          <SendHorizontal size={18} />
        </button>
      </div>
      <p className="text-[11px] text-text-muted text-center mt-2">
        Enter to send · Shift+Enter for new line
      </p>
    </div>
  );
}
