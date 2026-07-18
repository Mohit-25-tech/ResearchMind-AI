import { useState } from "react";
import { Library, Plus, MessageSquare, Trash2, LogOut, Search, Edit2, Settings } from "lucide-react";
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
  onRenameConversation: (id: number, title: string) => void;
  onClearAllDocuments: () => void;
  onClearAllConversations: () => void;
}

function getGroupLabel(dateStr: string): "Today" | "Yesterday" | "Last 7 Days" | "Earlier" {
  try {
    const parsedStr = dateStr.includes(" ") ? dateStr.replace(" ", "T") + "Z" : dateStr;
    const date = new Date(parsedStr);
    const now = new Date();
    
    const d1 = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    const d2 = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    
    const diffMs = d2.getTime() - d1.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays <= 7) return "Last 7 Days";
  } catch (e) {
    console.error("Date parsing error:", e);
  }
  return "Earlier";
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
  onRenameConversation,
  onClearAllDocuments,
  onClearAllConversations,
}: SidebarProps) {
  const { user, logout } = useAuth();
  
  // Local state for Search, Rename, and Menu triggers
  const [searchQuery, setSearchQuery] = useState("");
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingTitle, setEditingTitle] = useState("");
  const [deleteConfirmId, setDeleteConfirmId] = useState<number | null>(null);
  
  // Settings drop-down state
  const [showSettingsMenu, setShowSettingsMenu] = useState(false);
  const [showClearChatsConfirm, setShowClearChatsConfirm] = useState(false);
  const [showClearDocsConfirm, setShowClearDocsConfirm] = useState(false);

  // Filter conversations
  const filteredConversations = conversations.filter((c) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Group conversations
  const groups: { [key in "Today" | "Yesterday" | "Last 7 Days" | "Earlier"]?: Conversation[] } = {};
  filteredConversations.forEach((conv) => {
    const label = getGroupLabel(conv.updated_at || conv.created_at);
    if (!groups[label]) {
      groups[label] = [];
    }
    groups[label]?.push(conv);
  });

  const groupOrder: ("Today" | "Yesterday" | "Last 7 Days" | "Earlier")[] = [
    "Today",
    "Yesterday",
    "Last 7 Days",
    "Earlier",
  ];

  return (
    <aside className="flex flex-col h-full bg-surface border-r border-border relative select-none">
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
        All Documents
      </button>

      {/* Document list */}
      <div className="max-h-[25%] overflow-y-auto px-2 pb-2 mt-1 border-b border-border">
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

      {/* 2. Conversations Search & History */}
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

        {/* Search input box */}
        <div className="relative mb-3 px-1">
          <Search size={11} className="absolute left-3 top-2.5 text-text-faint" />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-7 pr-2.5 py-1.5 rounded-md border border-border bg-surface-elevated text-xs text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent/40"
          />
        </div>

        {filteredConversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-6 text-center text-text-faint">
            <MessageSquare size={16} className="mb-1" />
            <p className="text-[10px]">{searchQuery ? "No search matches." : "No conversations yet."}</p>
          </div>
        ) : (
          <div className="flex flex-col gap-3 min-h-0 overflow-y-auto">
            {groupOrder.map((groupKey) => {
              const list = groups[groupKey];
              if (!list || list.length === 0) return null;
              
              return (
                <div key={groupKey} className="flex flex-col gap-0.5">
                  <h3 className="text-[10px] font-semibold text-text-faint px-2 mb-1 uppercase tracking-wide">
                    {groupKey}
                  </h3>
                  {list.map((conv) => (
                    <div
                      key={conv.id}
                      onClick={() => editingId !== conv.id && onSelectConversation(conv.id)}
                      className={`group flex items-center justify-between px-2.5 py-1.5 rounded-md text-xs cursor-pointer sidebar-transition
                        ${
                          currentConversationId === conv.id
                            ? "bg-accent-subtle text-accent font-medium border-l-2 border-accent"
                            : "text-text-secondary hover:text-text-primary hover:bg-surface-hover border-l-2 border-transparent"
                        }`}
                    >
                      {editingId === conv.id ? (
                        <input
                          type="text"
                          value={editingTitle}
                          onChange={(e) => setEditingTitle(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") {
                              if (editingTitle.trim()) {
                                onRenameConversation(conv.id, editingTitle.trim());
                              }
                              setEditingId(null);
                            } else if (e.key === "Escape") {
                              setEditingId(null);
                            }
                          }}
                          onBlur={() => {
                            if (editingTitle.trim()) {
                              onRenameConversation(conv.id, editingTitle.trim());
                            }
                            setEditingId(null);
                          }}
                          autoFocus
                          className="flex-1 px-1 py-0.5 rounded border border-accent/40 bg-surface-elevated text-xs text-text-primary focus:outline-none"
                        />
                      ) : (
                        <>
                          <span className="truncate flex-1 pr-2">{conv.title}</span>
                          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all shrink-0">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setEditingId(conv.id);
                                setEditingTitle(conv.title);
                              }}
                              className="p-0.5 rounded text-text-muted hover:text-text-primary cursor-pointer"
                              title="Rename chat"
                            >
                              <Edit2 size={10} />
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setDeleteConfirmId(conv.id);
                              }}
                              className="p-0.5 rounded text-text-muted hover:text-error cursor-pointer"
                              title="Delete chat"
                            >
                              <Trash2 size={10} />
                            </button>
                          </div>
                        </>
                      )}
                    </div>
                  ))}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 3. User profile footer panel with Settings */}
      {user && (
        <div className="p-3 border-t border-border bg-surface-elevated/40 flex items-center gap-2 shrink-0 relative">
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
          
          {/* Settings Trigger */}
          <button
            onClick={() => setShowSettingsMenu(!showSettingsMenu)}
            className={`p-1.5 rounded-md text-text-muted hover:text-text-primary hover:bg-surface-hover transition-colors cursor-pointer shrink-0
              ${showSettingsMenu ? "bg-surface-hover text-text-primary" : ""}`}
            title="Settings"
          >
            <Settings size={13} />
          </button>
          
          {/* Settings Menu Dropdown */}
          {showSettingsMenu && (
            <div className="absolute bottom-14 right-3 z-50 w-48 bg-surface rounded-lg border border-border shadow-xl py-1 animate-in fade-in slide-in-from-bottom-2 duration-150">
              <button
                onClick={() => {
                  setShowSettingsMenu(false);
                  setShowClearChatsConfirm(true);
                }}
                className="w-full text-left px-3 py-2 text-xs text-text-secondary hover:text-text-primary hover:bg-surface-hover cursor-pointer"
              >
                Clear Chats History
              </button>
              <button
                onClick={() => {
                  setShowSettingsMenu(false);
                  setShowClearDocsConfirm(true);
                }}
                className="w-full text-left px-3 py-2 text-xs text-text-secondary hover:text-text-primary hover:bg-surface-hover cursor-pointer"
              >
                Clear Document Library
              </button>
              <div className="border-t border-border my-1" />
              <button
                onClick={() => {
                  setShowSettingsMenu(false);
                  logout();
                }}
                className="w-full text-left px-3 py-2 text-xs text-error hover:bg-error-subtle cursor-pointer flex items-center gap-1.5"
              >
                <LogOut size={12} />
                Log Out
              </button>
            </div>
          )}
        </div>
      )}

      {/* 4. Delete Single Conversation Modal */}
      {deleteConfirmId !== null && (
        <div className="fixed inset-0 z-50 bg-black/25 backdrop-blur-[1px] flex items-center justify-center p-4">
          <div className="bg-surface rounded-xl border border-border shadow-xl max-w-sm w-full p-5">
            <h3 className="text-sm font-semibold text-text-primary mb-2">Delete Conversation</h3>
            <p className="text-xs text-text-secondary mb-5">You are about to permanently delete this conversation.</p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setDeleteConfirmId(null)}
                className="px-3 py-1.5 rounded-lg border border-border text-xs text-text-secondary hover:bg-surface-hover cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  onDeleteConversation(deleteConfirmId);
                  setDeleteConfirmId(null);
                }}
                className="px-3 py-1.5 rounded-lg bg-error text-white text-xs hover:bg-red-600 cursor-pointer font-medium"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 5. Clear All Chats History Modal */}
      {showClearChatsConfirm && (
        <div className="fixed inset-0 z-50 bg-black/25 backdrop-blur-[1px] flex items-center justify-center p-4">
          <div className="bg-surface rounded-xl border border-border shadow-xl max-w-sm w-full p-5">
            <h3 className="text-sm font-semibold text-text-primary mb-2">Clear Conversation History</h3>
            <p className="text-xs text-text-secondary mb-5">You are about to permanently delete all conversations and message logs. This action cannot be undone.</p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowClearChatsConfirm(false)}
                className="px-3 py-1.5 rounded-lg border border-border text-xs text-text-secondary hover:bg-surface-hover cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  onClearAllConversations();
                  setShowClearChatsConfirm(false);
                }}
                className="px-3 py-1.5 rounded-lg bg-error text-white text-xs hover:bg-red-600 cursor-pointer font-medium"
              >
                Clear History
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 6. Clear All Documents Modal */}
      {showClearDocsConfirm && (
        <div className="fixed inset-0 z-50 bg-black/25 backdrop-blur-[1px] flex items-center justify-center p-4">
          <div className="bg-surface rounded-xl border border-border shadow-xl max-w-sm w-full p-5">
            <h3 className="text-sm font-semibold text-text-primary mb-2">Clear Document Library</h3>
            <p className="text-xs text-text-secondary mb-5">You are about to permanently delete all uploaded PDFs and vector indices from ChromaDB. You can re-upload them later.</p>
            <div className="flex justify-end gap-2">
              <button
                onClick={() => setShowClearDocsConfirm(false)}
                className="px-3 py-1.5 rounded-lg border border-border text-xs text-text-secondary hover:bg-surface-hover cursor-pointer"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  onClearAllDocuments();
                  setShowClearDocsConfirm(false);
                }}
                className="px-3 py-1.5 rounded-lg bg-error text-white text-xs hover:bg-red-600 cursor-pointer font-medium"
              >
                Clear Documents
              </button>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}
