import { useRef, useEffect, useCallback } from "react";
import {
  BrainCircuit,
  Upload,
  MessageSquare,
  BookMarked,
  Files,
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

const EXAMPLE_PROMPTS = [
  "Summarize this paper",
  "Explain the methodology",
  "Compare the results",
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
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const isNearBottomRef = useRef(true);

  // Track if user is near the bottom
  const handleScroll = useCallback(() => {
    const el = scrollContainerRef.current;
    if (!el) return;
    const threshold = 100;
    isNearBottomRef.current =
      el.scrollHeight - el.scrollTop - el.clientHeight < threshold;
  }, []);

  // Auto-scroll only if user is near bottom
  useEffect(() => {
    if (isNearBottomRef.current) {
      const el = scrollContainerRef.current;
      if (el) {
        el.scrollTop = el.scrollHeight;
      }
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
          <div className="flex items-center justify-center w-14 h-14 rounded-2xl bg-accent-subtle mb-5">
            <BrainCircuit size={28} className="text-accent" />
          </div>
          <h2 className="text-xl font-semibold text-text-primary mb-2">
            AI Research Assistant
          </h2>
          <p className="text-sm text-text-secondary mb-8 leading-relaxed">
            Upload research papers, ask questions, and receive cited answers.
          </p>

          {/* Feature highlights */}
          <div className="grid grid-cols-2 gap-3 w-full mb-8">
            {[
              { icon: Upload, label: "Upload research papers" },
              { icon: MessageSquare, label: "Ask questions" },
              { icon: BookMarked, label: "Receive cited answers" },
              { icon: Files, label: "Supports multiple PDFs" },
            ].map(({ icon: Icon, label }) => (
              <div
                key={label}
                className="flex items-center gap-2.5 rounded-xl bg-surface-elevated px-3.5 py-3 text-left"
              >
                <Icon size={15} className="text-accent shrink-0" />
                <span className="text-xs text-text-secondary">{label}</span>
              </div>
            ))}
          </div>

          {/* Example prompts */}
          <div className="w-full">
            <p className="text-xs text-text-muted mb-3">Try asking:</p>
            <div className="flex flex-col gap-2">
              {EXAMPLE_PROMPTS.map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => onSendExample(prompt)}
                  className="w-full text-left px-4 py-2.5 rounded-xl border border-border
                             text-sm text-text-secondary hover:text-text-primary
                             hover:bg-surface-hover hover:border-border-strong
                             transition-all cursor-pointer"
                >
                  "{prompt}"
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
      {/* Chat header with clear button */}
      {messages.length > 0 && (
        <div className="flex items-center justify-end px-4 py-2 border-b border-border">
          <button
            onClick={onClearChat}
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs
                       text-text-muted hover:text-error hover:bg-error-subtle
                       transition-colors cursor-pointer"
          >
            <Trash2 size={12} />
            Clear Chat
          </button>
        </div>
      )}

      {/* Messages */}
      <div
        ref={scrollContainerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto"
      >
        <div className="max-w-4xl mx-auto py-4">
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

      {/* Error */}
      {error && (
        <div className="px-4 pb-2">
          <ErrorMessage message={error} />
        </div>
      )}
    </div>
  );
}
