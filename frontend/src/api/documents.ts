import api from "./api";
import type { DocumentsResponse, UploadResponse, DeleteResponse } from "../types/document";

/**
 * Fetch all uploaded documents.
 * GET /documents — auto-retries once on failure via interceptor.
 */
export async function fetchDocuments(): Promise<DocumentsResponse> {
  const response = await api.get<DocumentsResponse>("/documents");
  return response.data;
}

/**
 * Upload a PDF document.
 * POST /upload — multipart form data with progress tracking.
 * Never auto-retried.
 */
export async function uploadDocument(
  file: File,
  onProgress?: (percent: number) => void,
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post<UploadResponse>("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (event) => {
      if (event.total && onProgress) {
        const percent = Math.round((event.loaded / event.total) * 100);
        onProgress(percent);
      }
    },
  });

  return response.data;
}

/**
 * Delete a document by ID.
 * DELETE /documents/{document_id} — never auto-retried.
 */
export async function deleteDocument(documentId: string): Promise<DeleteResponse> {
  const response = await api.delete<DeleteResponse>(`/documents/${documentId}`);
  return response.data;
}
