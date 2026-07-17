import { useRef, useEffect, useCallback } from "react";
import {
  BrainCircuit,
  Sparkles,
  Trash2,
} from "lucide-react";
import type { ChatMessage } from "../../types/chat";
import Message from "./Message";
import ErrorMessage from "../Common/ErrorMessage";

interface ChatBoxProps {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  onCopy: (id: string) => Promise<boolean>;
  onRegenerate: () => void;
  onClearChat: () => void;
  onSendExample: (prompt: string) => void;
}

const EXAMPLES = [
  "Summarize the key findings of this paper",
  "What methodology was used?",
  "Compare the results with previous work",
];

export default function ChatBox({
  messages,
  isLoading: _isLoading,
  error,
  onCopy,
  onRegenerate,
  onClearChat,
  onSendExample,
}: ChatBoxProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const isNearBottomRef = useRef(true);

  const handleScroll = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    isNearBottomRef.current =
      el.scrollHeight - el.scrollTop - el.clientHeight < 80;
  }, []);

  useEffect(() => {
    if (isNearBottomRef.current) {
      const el = scrollRef.current;
      if (el) el.scrollTop = el.scrollHeight;
    }
  }, [messages]);

  const lastAssistantIndex = messages.findLastIndex(
    (m) => m.role === "assistant",
  );

  // Welcome screen
  if (messages.length === 0 && !error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center px-6">
        <div className="flex flex-col items-center max-w-md text-center">
          <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-accent-subtle mb-4">
            <BrainCircuit size={20} className="text-accent" />
          </div>
          <h2 className="text-lg font-semibold text-text-primary mb-1">
            AI Research Assistant
          </h2>
          <p className="text-xs text-text-muted mb-8 leading-relaxed max-w-xs">
            Upload research papers and ask questions.
            Every answer includes source citations.
          </p>

          <div className="w-full max-w-sm">
            <p className="text-[10px] text-text-faint uppercase tracking-wider mb-2.5 flex items-center gap-1">
              <Sparkles size={10} />
              Try asking
            </p>
            <div className="flex flex-col gap-1.5">
              {EXAMPLES.map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => onSendExample(prompt)}
                  className="w-full text-left px-3.5 py-2.5 rounded-lg border border-border
                             text-xs text-text-muted hover:text-text-secondary
                             hover:bg-surface-elevated hover:border-border-strong
                             transition-all cursor-pointer"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col min-h-0">
      {/* Clear chat */}
      {messages.length > 0 && (
        <div className="flex items-center justify-end px-4 py-1.5 border-b border-border">
          <button
            onClick={onClearChat}
            className="flex items-center gap-1 px-2 py-1 rounded-md text-[11px]
                       text-text-muted hover:text-error hover:bg-error-subtle
                       transition-colors cursor-pointer"
          >
            <Trash2 size={11} />
            Clear
          </button>
        </div>
      )}

      {/* Messages */}
      <div
        ref={scrollRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto"
      >
        <div className="max-w-3xl mx-auto py-4">
          {messages.map((msg, index) => (
            <Message
              key={msg.id}
              message={msg}
              isLast={index === lastAssistantIndex}
              onCopy={onCopy}
              onRegenerate={onRegenerate}
            />
          ))}
        </div>
      </div>

      {error && (
        <div className="px-4 pb-2">
          <ErrorMessage message={error} />
        </div>
      )}
    </div>
  );
}
