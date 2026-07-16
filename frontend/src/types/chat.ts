export interface Source {
  document_id: string;
  filename: string;
  pages: number[];
}

export interface ChatResponse {
  session_id: string;
  answer: string;
  sources: Source[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  isTyping?: boolean;
}
