import { useRef, useEffect, useCallback } from "react";
import { ArrowUp } from "lucide-react";

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
