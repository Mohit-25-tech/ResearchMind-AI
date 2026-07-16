import { useState } from "react";
import { FileText, Trash2, Layers, BookOpen, Clock } from "lucide-react";
import type { Document } from "../../types/document";
import { formatDate } from "../../utils/formatDate";

interface DocumentCardProps {
  document: Document;
  isSelected: boolean;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
}

export default function DocumentCard({
  document,
  isSelected,
  onSelect,
  onDelete,
}: DocumentCardProps) {
  const [showConfirm, setShowConfirm] = useState(false);

  function handleDelete(e: React.MouseEvent) {
    e.stopPropagation();
    if (showConfirm) {
      onDelete(document.document_id);
      setShowConfirm(false);
    } else {
      setShowConfirm(true);
    }
  }

  function handleCancelDelete(e: React.MouseEvent) {
    e.stopPropagation();
    setShowConfirm(false);
  }

  return (
    <div
      onClick={() => onSelect(document.document_id)}
      className={`group relative rounded-lg p-3 cursor-pointer transition-all duration-150
        border
        ${
          isSelected
            ? "border-accent/40 bg-accent-subtle"
            : "border-transparent hover:bg-surface-hover"
        }`}
    >
      {/* Header row: icon + filename + delete */}
      <div className="flex items-start gap-2.5">
        <FileText
          size={16}
          className={`mt-0.5 shrink-0 ${
            isSelected ? "text-accent" : "text-text-muted"
          }`}
        />
        <div className="flex-1 min-w-0">
          <p
            className={`text-sm font-medium truncate ${
              isSelected ? "text-accent-hover" : "text-text-primary"
            }`}
            title={document.filename}
          >
            {document.filename}
          </p>
        </div>

        {/* Delete button */}
        {!showConfirm && (
          <button
            onClick={handleDelete}
            className="opacity-0 group-hover:opacity-100 p-1 rounded transition-all
                       text-text-muted hover:text-error hover:bg-error-subtle cursor-pointer"
            title="Delete document"
          >
            <Trash2 size={13} />
          </button>
        )}
      </div>

      {/* Meta row */}
      <div className="flex items-center gap-3 mt-2 ml-[26px]">
        <span className="flex items-center gap-1 text-xs text-text-muted">
          <BookOpen size={11} />
          {document.pages} pages
        </span>
        <span className="flex items-center gap-1 text-xs text-text-muted">
          <Layers size={11} />
          {document.chunks} chunks
        </span>
      </div>

      {/* Upload time */}
      <div className="flex items-center gap-1 mt-1.5 ml-[26px]">
        <Clock size={10} className="text-text-muted" />
        <span className="text-[11px] text-text-muted">
          {formatDate(document.uploaded_at)}
        </span>
      </div>

      {/* Inline delete confirmation */}
      {showConfirm && (
        <div
          className="flex items-center gap-2 mt-2 ml-[26px]"
          onClick={(e) => e.stopPropagation()}
        >
          <span className="text-xs text-text-secondary">Delete?</span>
          <button
            onClick={handleDelete}
            className="text-xs text-error hover:text-red-400 font-medium cursor-pointer"
          >
            Yes
          </button>
          <button
            onClick={handleCancelDelete}
            className="text-xs text-text-muted hover:text-text-secondary cursor-pointer"
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}
