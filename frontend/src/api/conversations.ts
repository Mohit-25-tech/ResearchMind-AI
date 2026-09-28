import api from "./api";

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  selected_document_ids?: string[];
}

export interface ConversationDetail {
  messages: {
    role: "user" | "assistant";
    content: string;
    created_at: string;
  }[];
  selected_document_ids?: string[];
}

export async function fetchConversations(): Promise<Conversation[]> {
  const response = await api.get<{ conversations: Conversation[] }>("/conversations");
  return response.data.conversations;
}

export async function fetchConversationMessages(id: number): Promise<ConversationDetail> {
  const response = await api.get<ConversationDetail>(`/conversations/${id}`);
  return response.data;
}

export async function deleteConversation(id: number): Promise<void> {
  await api.delete(`/conversations/${id}`);
}

export async function renameConversation(id: number, title: string): Promise<void> {
  await api.patch(`/conversations/${id}`, { title });
}

export async function updateConversationDocuments(id: number, documentIds: string[]): Promise<void> {
  await api.patch(`/conversations/${id}/documents`, { document_ids: documentIds });
}

export async function clearConversations(): Promise<void> {
  await api.delete("/conversations");
}
