import { Library, Plus, MessageSquare, Trash2, LogOut } from "lucide-react";
import UploadButton from "../Documents/UploadButton";
import DocumentList from "../Documents/DocumentList";
import type { Document } from "../../types/document";
import type { Conversation } from "../../api/conversations";
import { useAuth } from "../../context/AuthContext";

interface SidebarProps {
  documents: Document[];
  isLoading: boolean;
  error: string | null;
  selectedDocumentId: string | null;
  isUploading: boolean;
  uploadProgress: number | null;
  uploadError: string | null;
  onUpload: (file: File) => void;
  onSelect: (id: string | null) => void;
  onDelete: (id: string) => void;
  onRetryFetch: () => void;
  
  // Conversations parameters
  conversations: Conversation[];
  currentConversationId: number | null;
  onSelectConversation: (id: number | null) => void;
  onDeleteConversation: (id: number) => void;
}

export default function Sidebar({
  documents,
  isLoading,
  error,
  selectedDocumentId,
  isUploading,
  uploadProgress,
  uploadError,
  onUpload,
  onSelect,
  onDelete,
  onRetryFetch,
  
  conversations,
  currentConversationId,
  onSelectConversation,
  onDeleteConversation,
}: SidebarProps) {
  const { user, logout } = useAuth();

  return (
    <aside className="flex flex-col h-full bg-surface border-r border-border">
      {/* 1. Header & Document Library */}
      <div className="px-3 pt-3 pb-2">
        <div className="flex items-center justify-between mb-2.5">
          <h2 className="text-[11px] font-semibold text-text-muted uppercase tracking-wider flex items-center gap-1.5">
            <Library size={12} />
            Research Library
          </h2>
          <span className="text-[10px] text-text-faint tabular-nums">
            {documents.length}
          </span>
        </div>
        <UploadButton
          isUploading={isUploading}
          uploadProgress={uploadProgress}
          uploadError={uploadError}
          onUpload={onUpload}
        />
      </div>

      {/* All Documents filter */}
      <button
        onClick={() => onSelect(null)}
        className={`mx-2 px-2.5 py-1.5 rounded-md text-xs text-left transition-colors cursor-pointer flex items-center gap-1.5
          ${
            selectedDocumentId === null
              ? "bg-accent-subtle text-accent font-medium"
              : "text-text-secondary hover:text-text-primary hover:bg-surface-hover"
          }`}
      >
        <Plus size={11} className="rotate-45 opacity-0" />
        All Documents
      </button>

      {/* Document list */}
      <div className="max-h-[30%] overflow-y-auto px-2 pb-2 mt-1 border-b border-border">
        <DocumentList
          documents={documents}
          isLoading={isLoading}
          error={error}
          selectedDocumentId={selectedDocumentId}
          onSelect={onSelect}
          onDelete={onDelete}
          onRetry={onRetryFetch}
        />
      </div>

      {/* 2. Conversations History */}
      <div className="flex-1 overflow-y-auto px-2 py-3 flex flex-col min-h-0">
        <div className="flex items-center justify-between px-1 mb-2">
          <h2 className="text-[11px] font-semibold text-text-muted uppercase tracking-wider flex items-center gap-1.5">
            <MessageSquare size={12} />
            Conversations
          </h2>
          <button
            onClick={() => onSelectConversation(null)}
            className="text-[10px] text-accent hover:text-accent-hover font-medium flex items-center gap-0.5 cursor-pointer"
            title="Start new chat"
          >
            <Plus size={10} />
            New
          </button>
        </div>

        {conversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-6 text-center text-text-faint">
            <MessageSquare size={16} className="mb-1" />
            <p className="text-[10px]">No chat history.</p>
          </div>
        ) : (
          <div className="flex flex-col gap-0.5 min-h-0 overflow-y-auto">
            {conversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => onSelectConversation(conv.id)}
                className={`group flex items-center justify-between px-2 py-1.5 rounded-md text-xs cursor-pointer transition-colors
                  ${
                    currentConversationId === conv.id
                      ? "bg-accent-subtle text-accent font-medium"
                      : "text-text-secondary hover:text-text-primary hover:bg-surface-hover"
                  }`}
              >
                <span className="truncate flex-1 pr-2">{conv.title}</span>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteConversation(conv.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-0.5 rounded text-text-muted hover:text-error transition-all cursor-pointer"
                  title="Delete chat"
                >
                  <Trash2 size={11} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 3. User profile footer panel */}
      {user && (
        <div className="p-3 border-t border-border bg-surface-elevated/40 flex items-center gap-2 shrink-0">
          <img
            src={user.picture || "https://lh3.googleusercontent.com/a/default-user"}
            alt={user.name}
            referrerPolicy="no-referrer"
            className="w-8 h-8 rounded-full border border-border object-cover"
          />
          <div className="min-w-0 flex-1">
            <p className="text-xs font-semibold text-text-primary truncate">{user.name}</p>
            <p className="text-[10px] text-text-muted truncate">{user.email}</p>
          </div>
          <button
            onClick={logout}
            className="p-1.5 rounded-md text-text-muted hover:text-error hover:bg-error-subtle transition-colors cursor-pointer shrink-0"
            title="Log Out"
          >
            <LogOut size={13} />
          </button>
        </div>
      )}
    </aside>
  );
}
