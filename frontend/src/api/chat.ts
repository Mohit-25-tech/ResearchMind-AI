import api from "./api";
import type { ChatResponse } from "../types/chat";

/**
 * Send a chat message.
 * POST /chat?question=...&session_id=...&document_id=...
 *
 * Uses query parameters (not JSON body) to match the FastAPI endpoint.
 * Accepts an AbortSignal for request cancellation.
 */
export async function sendChatMessage(
  question: string,
  sessionId: string,
  documentId?: string | null,
  signal?: AbortSignal,
): Promise<ChatResponse> {
  const params: Record<string, string> = {
    question,
    session_id: sessionId,
  };

  if (documentId) {
    params.document_id = documentId;
  }

  const response = await api.post<ChatResponse>("/chat", null, {
    params,
    signal,
  });

  return response.data;
}
