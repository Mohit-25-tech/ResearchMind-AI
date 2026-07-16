import { useState, useEffect, useCallback } from "react";
import type { Document } from "../types/document";
import {
  fetchDocuments,
  uploadDocument,
  deleteDocument,
} from "../api/documents";

const SELECTED_DOC_KEY = "ai-research-selected-document";

export function useDocuments() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Restore selected document from localStorage
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(
    () => localStorage.getItem(SELECTED_DOC_KEY),
  );

  const fetchDocs = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchDocuments();
      setDocuments(data.documents);
    } catch {
      setError("Failed to fetch documents. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Auto-fetch on mount
  useEffect(() => {
    fetchDocs();
  }, [fetchDocs]);

  const selectDocument = useCallback((id: string | null) => {
    setSelectedDocumentId(id);
    if (id) {
      localStorage.setItem(SELECTED_DOC_KEY, id);
    } else {
      localStorage.removeItem(SELECTED_DOC_KEY);
    }
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedDocumentId(null);
    localStorage.removeItem(SELECTED_DOC_KEY);
  }, []);

  const upload = useCallback(
    async (file: File) => {
      setIsUploading(true);
      setUploadProgress(0);
      setUploadError(null);
      try {
        await uploadDocument(file, (percent) => {
          setUploadProgress(percent);
        });
        // Refresh document list after successful upload
        await fetchDocs();
      } catch {
        setUploadError("Upload failed. Please try again.");
      } finally {
        setIsUploading(false);
        setUploadProgress(null);
      }
    },
    [fetchDocs],
  );

  const remove = useCallback(
    async (id: string) => {
      try {
        await deleteDocument(id);
        // If the deleted doc was selected, clear selection
        if (selectedDocumentId === id) {
          clearSelection();
        }
        // Refresh document list
        await fetchDocs();
      } catch {
        setError("Failed to delete document. Please try again.");
      }
    },
    [fetchDocs, selectedDocumentId, clearSelection],
  );

  return {
    documents,
    isLoading,
    error,
    selectedDocumentId,
    selectDocument,
    clearSelection,
    upload,
    remove,
    fetchDocs,
    isUploading,
    uploadProgress,
    uploadError,
  };
}
