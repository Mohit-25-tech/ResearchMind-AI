import api from "./api";
import type { ChatResponse } from "../types/chat";

/**
 * Send a chat message.
 * POST /chat?question=...&session_id=...&document_ids=...
 *
 * Uses query parameters (not JSON body) to match the FastAPI endpoint.
 * Accepts an AbortSignal for request cancellation.
 */
export async function sendChatMessage(
  question: string,
  sessionId: string,
  documentIds?: string[] | string | null,
  signal?: AbortSignal,
): Promise<ChatResponse> {
  const searchParams = new URLSearchParams();
  searchParams.append("question", question);
  searchParams.append("session_id", sessionId);

  const ids: string[] = Array.isArray(documentIds)
    ? documentIds
    : documentIds
    ? [documentIds]
    : [];

  ids.forEach((id) => searchParams.append("document_ids", id));
  if (ids.length > 0) {
    searchParams.append("document_id", ids[0]);
  }

  const response = await api.post<ChatResponse>(`/chat?${searchParams.toString()}`, null, {
    signal,
  });

  return response.data;
}
