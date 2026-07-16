import { Library } from "lucide-react";
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
    <aside className="flex flex-col h-full border-r border-border bg-surface">
      {/* Header */}
      <div className="px-4 py-3.5 border-b border-border">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-text-primary flex items-center gap-2">
            <Library size={15} className="text-text-secondary" />
            Documents
          </h2>
          <span className="text-xs text-text-muted tabular-nums">
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
        className={`mx-3 mt-3 mb-1 px-3 py-2 rounded-lg text-xs font-medium text-left transition-colors cursor-pointer
          ${
            selectedDocumentId === null
              ? "bg-accent-subtle text-accent"
              : "text-text-secondary hover:text-text-primary hover:bg-surface-hover"
          }`}
      >
        All Documents
      </button>

      {/* Document list */}
      <div className="flex-1 overflow-y-auto px-3 pb-3">
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
