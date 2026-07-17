import { Library, Plus } from "lucide-react";
import UploadButton from "../Documents/UploadButton";
import DocumentList from "../Documents/DocumentList";
import type { Document } from "../../types/document";

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
}: SidebarProps) {
  return (
    <aside className="flex flex-col h-full bg-surface">
      {/* Header */}
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
      <div className="flex-1 overflow-y-auto px-2 pb-2 mt-1">
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
    </aside>
  );
}
