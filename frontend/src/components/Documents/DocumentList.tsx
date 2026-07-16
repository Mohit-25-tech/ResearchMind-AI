import { FileText } from "lucide-react";
import type { Document } from "../../types/document";
import DocumentCard from "./DocumentCard";
import Loading from "../Common/Loading";
import ErrorMessage from "../Common/ErrorMessage";
import EmptyState from "../Common/EmptyState";

interface DocumentListProps {
  documents: Document[];
  isLoading: boolean;
  error: string | null;
  selectedDocumentId: string | null;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  onRetry: () => void;
}

export default function DocumentList({
  documents,
  isLoading,
  error,
  selectedDocumentId,
  onSelect,
  onDelete,
  onRetry,
}: DocumentListProps) {
  if (isLoading) {
    return <Loading text="Fetching documents..." size={18} />;
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={onRetry} />;
  }

  if (documents.length === 0) {
    return (
      <EmptyState
        icon={<FileText size={32} />}
        title="Upload your first research paper."
        subtitle="Supports PDF documents."
      />
    );
  }

  return (
    <div className="flex flex-col gap-1 mt-1">
      {documents.map((doc) => (
        <DocumentCard
          key={doc.document_id}
          document={doc}
          isSelected={selectedDocumentId === doc.document_id}
          onSelect={onSelect}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
