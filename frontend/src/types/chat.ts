export interface Source {
  document_id: string;
  filename: string;
  pages: number[];
  url?: string;
}

export interface ChatResponse {
  session_id: string;
  answer: string;
  sources: Source[];
  trace?: string[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  trace?: string[];
  isTyping?: boolean;
}
