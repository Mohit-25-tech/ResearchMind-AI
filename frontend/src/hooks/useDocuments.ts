import { useState, useEffect, useCallback } from "react";
import type { Document } from "../types/document";
import {
  fetchDocuments,
  uploadDocument,
  deleteDocument,
  clearAllDocuments,
} from "../api/documents";

const SELECTED_DOCS_KEY = "ai-research-selected-documents";

export function useDocuments() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Restore selected documents from localStorage
  const [selectedDocumentIds, setSelectedDocumentIdsState] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem(SELECTED_DOCS_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        return Array.isArray(parsed) ? parsed : [];
      }
      // Backwards compatibility with single doc key
      const single = localStorage.getItem("ai-research-selected-document");
      return single ? [single] : [];
    } catch {
      return [];
    }
  });

  const fetchDocs = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchDocuments();
      setDocuments(data.documents);
    } catch {
      setError("Failed to load documents. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocs();
  }, [fetchDocs]);

  const setSelectedDocumentIds = useCallback((ids: string[]) => {
    setSelectedDocumentIdsState(ids);
    try {
      localStorage.setItem(SELECTED_DOCS_KEY, JSON.stringify(ids));
    } catch {
      // ignore
    }
  }, []);

  const toggleDocument = useCallback((id: string) => {
    setSelectedDocumentIdsState((prev) => {
      const next = prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id];
      try {
        localStorage.setItem(SELECTED_DOCS_KEY, JSON.stringify(next));
      } catch {
        // ignore
      }
      return next;
    });
  }, []);

  const selectDocument = useCallback((id: string | null) => {
    if (!id) {
      setSelectedDocumentIds([]);
    } else {
      toggleDocument(id);
    }
  }, [setSelectedDocumentIds, toggleDocument]);

  const clearSelection = useCallback(() => {
    setSelectedDocumentIds([]);
  }, [setSelectedDocumentIds]);

  const selectedDocumentId = selectedDocumentIds[0] ?? null;

  const upload = useCallback(
    async (file: File) => {
      setIsUploading(true);
      setUploadProgress(0);
      setUploadError(null);
      try {
        await uploadDocument(file, (percent) => {
          setUploadProgress(percent);
        });
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
        setSelectedDocumentIdsState((prev) => {
          const next = prev.filter((d) => d !== id);
          try {
            localStorage.setItem(SELECTED_DOCS_KEY, JSON.stringify(next));
          } catch {
            // ignore
          }
          return next;
        });
        await fetchDocs();
      } catch {
        setError("Failed to delete document. Please try again.");
      }
    },
    [fetchDocs],
  );

  const clearAllDocs = useCallback(async () => {
    try {
      await clearAllDocuments();
      clearSelection();
      await fetchDocs();
    } catch {
      setError("Failed to clear documents. Please try again.");
    }
  }, [fetchDocs, clearSelection]);

  return {
    documents,
    isLoading,
    error,
    selectedDocumentId,
    selectedDocumentIds,
    setSelectedDocumentIds,
    toggleDocument,
    selectDocument,
    clearSelection,
    upload,
    remove,
    fetchDocs,
    isUploading,
    uploadProgress,
    uploadError,
    clearAllDocs,
  };
}
