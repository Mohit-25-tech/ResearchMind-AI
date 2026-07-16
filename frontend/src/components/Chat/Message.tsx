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

  // Thinking state — assistant placeholder with no content yet
  if (isAssistant && message.isTyping && message.content === "") {
    return (
      <div className="flex gap-3 px-6 py-4">
        <div className="flex items-center justify-center w-7 h-7 rounded-lg bg-accent-subtle shrink-0 mt-0.5">
          <BrainCircuit size={14} className="text-accent" />
        </div>
        <div className="flex items-center gap-1.5 pt-1.5">
          <span className="text-sm text-text-secondary">Thinking</span>
          <span className="flex gap-0.5">
            <span className="w-1.5 h-1.5 rounded-full bg-text-muted loading-dot" />
            <span className="w-1.5 h-1.5 rounded-full bg-text-muted loading-dot" />
            <span className="w-1.5 h-1.5 rounded-full bg-text-muted loading-dot" />
          </span>
        </div>
      </div>
    );
  }

  return (
    <div
      className={`flex gap-3 px-6 py-4 ${
        isUser ? "flex-row-reverse" : ""
      }`}
    >
      {/* Avatar */}
      <div
        className={`flex items-center justify-center w-7 h-7 rounded-lg shrink-0 mt-0.5 ${
          isUser
            ? "bg-user-bubble"
            : "bg-accent-subtle"
        }`}
      >
        {isUser ? (
          <User size={14} className="text-user-bubble-text" />
        ) : (
          <BrainCircuit size={14} className="text-accent" />
        )}
      </div>

      {/* Content */}
      <div
        className={`max-w-[75%] ${isUser ? "text-right" : ""}`}
      >
        <div
          className={`inline-block rounded-2xl px-4 py-2.5 ${
            isUser
              ? "bg-user-bubble text-user-bubble-text rounded-tr-md"
              : "bg-surface-elevated text-text-primary rounded-tl-md"
          }`}
        >
          {isUser ? (
            <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
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

        {/* Action buttons for assistant messages */}
        {isAssistant && !message.isTyping && message.content && (
          <div className="flex items-center gap-1 mt-1.5">
            <button
              onClick={handleCopy}
              className="flex items-center gap-1 px-2 py-1 rounded-md text-xs
                         text-text-muted hover:text-text-secondary hover:bg-surface-hover
                         transition-colors cursor-pointer"
              title="Copy answer"
            >
              {copied ? (
                <>
                  <Check size={12} className="text-success" />
                  <span className="text-success">Copied</span>
                </>
              ) : (
                <>
                  <Copy size={12} />
                  <span>Copy</span>
                </>
              )}
            </button>

            {isLast && (
              <button
                onClick={onRegenerate}
                className="flex items-center gap-1 px-2 py-1 rounded-md text-xs
                           text-text-muted hover:text-text-secondary hover:bg-surface-hover
                           transition-colors cursor-pointer"
                title="Regenerate response"
              >
                <RefreshCw size={12} />
                <span>Regenerate</span>
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
