export interface Document {
  document_id: string;
  filename: string;
  pages: number;
  chunks: number;
  uploaded_at: string;
}

export interface DocumentsResponse {
  total_documents: number;
  documents: Document[];
}

export interface UploadResponse {
  message: string;
  filename: string;
  document_id: string;
  file_hash: string;
  chunks_created: number;
}

export interface DeleteResponse {
  message: string;
  document_id: string;
}
