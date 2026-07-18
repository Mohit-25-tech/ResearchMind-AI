import { useRef, useEffect, useCallback } from "react";
import {
  BrainCircuit,
  Trash2,
} from "lucide-react";
import type { ChatMessage } from "../../types/chat";
import type { Document } from "../../types/document";
import Message from "./Message";
import ErrorMessage from "../Common/ErrorMessage";
import { useAuth } from "../../context/AuthContext";

interface ChatBoxProps {
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  onCopy: (id: string) => Promise<boolean>;
  onRegenerate: () => void;
  onClearChat: () => void;
  onSendExample: (prompt: string) => void;
  documents: Document[];
  hasConversations: boolean;
  onUpload?: (file: File) => void;
  onSelectDocument: (id: string | null) => void;
}

export default function ChatBox({
  messages,
  isLoading: _isLoading,
  error,
  onCopy,
  onRegenerate,
  onClearChat,
  onSendExample,
  documents,
  hasConversations,
  onUpload,
  onSelectDocument,
}: ChatBoxProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const isNearBottomRef = useRef(true);
  const { user } = useAuth();
  const userName = user?.name || "Researcher";

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

  // Welcoming onboarding experience
  if (messages.length === 0 && !error) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-12 overflow-y-auto max-w-4xl mx-auto w-full animate-in fade-in duration-300">
        <div className="flex flex-col items-center max-w-2xl text-center mb-8 shrink-0">
          <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-accent-subtle mb-4">
            <BrainCircuit size={24} className="text-accent" />
          </div>
          <h1 className="text-2xl font-bold text-text-primary mb-2 tracking-tight">
            {hasConversations ? "📚 Continue your research" : `👋 Welcome, ${userName}`}
          </h1>
          <p className="text-xs text-text-muted max-w-md leading-relaxed">
            Your AI-powered research workspace.
            Upload research papers, ask questions, explore ideas, and discover insights from your documents.
          </p>
        </div>

        {/* DOCUMENTS EMPTY STATE OR SUGGESTED ACTIONS */}
        {documents.length === 0 ? (
          <div className="w-full max-w-md p-6 rounded-xl border border-border bg-surface-elevated/50 flex flex-col items-center text-center">
            <span className="text-2xl mb-2">📄</span>
            <h3 className="text-xs font-semibold text-text-primary mb-1">No research papers uploaded yet</h3>
            <p className="text-[11px] text-text-muted mb-4 leading-normal">
              Upload your first PDF to begin chatting with your research assistant.
            </p>
            <input
              type="file"
              accept=".pdf,application/pdf"
              id="welcome-file-upload"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file && onUpload) onUpload(file);
              }}
            />
            <button
              onClick={() => document.getElementById("welcome-file-upload")?.click()}
              className="px-4 py-2 bg-accent hover:bg-accent-hover text-white text-xs font-medium rounded-lg shadow-sm cursor-pointer transition-all premium-btn"
            >
              Upload PDF
            </button>
          </div>
        ) : (
          <div className="w-full flex flex-col gap-6">
            {/* Suggested Questions */}
            <div>
              <h3 className="text-[10px] font-semibold text-text-muted uppercase tracking-wider mb-3 text-center">
                Suggested Questions
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
                {[
                  { text: "Summarize this paper", icon: "📄" },
                  { text: "Explain the methodology", icon: "🔬" },
                  { text: "What are the key findings", icon: "📈" },
                  { text: "What are the limitations", icon: "⚠️" },
                  { text: "Explain this paper simply", icon: "💡" },
                  { text: "Compare with previous work", icon: "🔍" },
                ].map((item) => (
                  <button
                    key={item.text}
                    onClick={() => onSendExample(item.text)}
                    className="flex items-center gap-2 text-left p-3.5 rounded-xl border border-border bg-surface text-xs text-text-secondary hover:text-text-primary hover:bg-surface-hover hover:border-border-strong hover:scale-[1.02] hover:shadow-sm transition-all duration-200 cursor-pointer"
                  >
                    <span>{item.icon}</span>
                    <span className="truncate">{item.text}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Recent Documents */}
            <div>
              <h3 className="text-[10px] font-semibold text-text-muted uppercase tracking-wider mb-3 text-center">
                Recent Documents
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-2.5">
                {documents.slice(0, 3).map((doc) => (
                  <div
                    key={doc.document_id}
                    onClick={() => onSelectDocument(doc.document_id)}
                    className="p-3.5 rounded-xl border border-border bg-surface hover:bg-surface-hover hover:border-border-strong hover:scale-[1.01] transition-all cursor-pointer flex flex-col justify-between"
                  >
                    <div className="flex items-center gap-2 mb-2 truncate">
                      <span className="text-xs">📄</span>
                      <p className="text-xs font-medium text-text-primary truncate" title={doc.filename}>
                        {doc.filename}
                      </p>
                    </div>
                    <div className="flex items-center justify-between text-[10px] text-text-muted">
                      <span>{doc.pages} pages</span>
                      <span>{new Date(doc.uploaded_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Empty Conversation Warning */}
        {!hasConversations && (
          <p className="text-[10px] text-text-faint mt-10">
            💬 No conversations yet. Start asking questions about your research.
          </p>
        )}
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
