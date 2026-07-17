import { useState } from "react";
import { BrainCircuit, User, Copy, Check, RefreshCw } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import type { ChatMessage } from "../../types/chat";

interface MessageProps {
  message: ChatMessage;
  isLast: boolean;
  onCopy: (id: string) => Promise<boolean>;
  onRegenerate: () => void;
}

export default function Message({
  message,
  isLast,
  onCopy,
  onRegenerate,
}: MessageProps) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";
  const isAssistant = message.role === "assistant";

  async function handleCopy() {
    const success = await onCopy(message.id);
    if (success) {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  }

  // Thinking state
  if (isAssistant && message.isTyping && message.content === "") {
    return (
      <div className="flex gap-3 px-5 py-3">
        <div className="flex items-center justify-center w-6 h-6 rounded-md bg-accent-subtle shrink-0 mt-0.5">
          <BrainCircuit size={12} className="text-accent" />
        </div>
        <div className="flex items-center gap-1.5 pt-1">
          <span className="text-xs text-text-muted">Thinking</span>
          <span className="flex gap-0.5">
            <span className="w-1 h-1 rounded-full bg-text-muted loading-dot" />
            <span className="w-1 h-1 rounded-full bg-text-muted loading-dot" />
            <span className="w-1 h-1 rounded-full bg-text-muted loading-dot" />
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className={`flex gap-3 px-5 py-3 ${isUser ? "flex-row-reverse" : ""}`}>
      {/* Avatar */}
      <div
        className={`flex items-center justify-center w-6 h-6 rounded-md shrink-0 mt-0.5 ${
          isUser ? "bg-user-bubble" : "bg-accent-subtle"
        }`}
      >
        {isUser ? (
          <User size={12} className="text-user-bubble-text" />
        ) : (
          <BrainCircuit size={12} className="text-accent" />
        )}
      </div>

      {/* Content */}
      <div className={`min-w-0 max-w-[80%] ${isUser ? "text-right" : ""}`}>
        <div
          className={`inline-block rounded-xl px-3.5 py-2 ${
            isUser
              ? "bg-user-bubble text-user-bubble-text rounded-tr-sm"
              : "bg-surface-elevated text-text-primary rounded-tl-sm"
          }`}
        >
          {isUser ? (
            <p className="text-[13px] leading-relaxed whitespace-pre-wrap">{message.content}</p>
          ) : (
            <div className={`prose-chat ${message.isTyping ? "typing-cursor" : ""}`}>
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeHighlight]}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
        </div>

        {/* Actions */}
        {isAssistant && !message.isTyping && message.content && (
          <div className="flex items-center gap-0.5 mt-1">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px]
                         text-text-muted hover:text-text-secondary hover:bg-surface-hover
                         transition-colors cursor-pointer"
              title="Copy"
            >
              {copied ? (
                <>
                  <Check size={10} className="text-success" />
                  <span className="text-success">Copied</span>
                </>
              ) : (
                <>
                  <Copy size={10} />
                  <span>Copy</span>
                </>
              )}
            </button>

            {isLast && (
              <button
                onClick={onRegenerate}
                className="flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px]
                           text-text-muted hover:text-text-secondary hover:bg-surface-hover
                           transition-colors cursor-pointer"
                title="Regenerate"
              >
                <RefreshCw size={10} />
                <span>Retry</span>
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
