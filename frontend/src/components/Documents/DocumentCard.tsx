import { useState } from "react";
import { motion } from "framer-motion";
import { FileText, Trash2, BookOpen, Layers, Clock } from "lucide-react";
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
    <motion.div
      layout
      initial={{ opacity: 0, y: 4 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -4 }}
      onClick={() => onSelect(document.document_id)}
      className={`group relative rounded-md px-2.5 py-2 cursor-pointer sidebar-transition
        ${
          isSelected
            ? "bg-accent-subtle border-l-2 border-accent font-medium shadow-sm"
            : "hover:bg-surface-hover border-l-2 border-transparent"
        }`}
    >
      {/* Header: icon + filename + delete */}
      <div className="flex items-center gap-2">
        <FileText
          size={13}
          className={`shrink-0 ${isSelected ? "text-accent" : "text-text-muted"}`}
        />
        <p
          className={`text-xs font-medium truncate flex-1 ${
            isSelected ? "text-accent-hover" : "text-text-primary"
          }`}
          title={document.filename}
        >
          {document.filename}
        </p>
        {!showConfirm && (
          <button
            onClick={handleDelete}
            className="opacity-0 group-hover:opacity-100 p-0.5 rounded transition-all
                       text-text-muted hover:text-error cursor-pointer"
            title="Delete"
          >
            <Trash2 size={11} />
          </button>
        )}
      </div>

      {/* Meta */}
      <div className="flex items-center gap-2.5 mt-1 ml-[21px]">
        <span className="flex items-center gap-0.5 text-[10px] text-text-muted">
          <BookOpen size={9} />
          {document.pages}p
        </span>
        <span className="flex items-center gap-0.5 text-[10px] text-text-muted">
          <Layers size={9} />
          {document.chunks}c
        </span>
        <span className="flex items-center gap-0.5 text-[10px] text-text-muted">
          <Clock size={9} />
          {formatDate(document.uploaded_at)}
        </span>
      </div>

      {/* Delete confirmation */}
      {showConfirm && (
        <div
          className="flex items-center gap-2 mt-1.5 ml-[21px]"
          onClick={(e) => e.stopPropagation()}
        >
          <span className="text-[10px] text-text-secondary">Delete?</span>
          <button
            onClick={handleDelete}
            className="text-[10px] text-error hover:text-red-400 font-medium cursor-pointer"
          >
            Yes
          </button>
          <button
            onClick={handleCancelDelete}
            className="text-[10px] text-text-muted hover:text-text-secondary cursor-pointer"
          >
            No
          </button>
        </div>
      )}
    </motion.div>
  );
}
