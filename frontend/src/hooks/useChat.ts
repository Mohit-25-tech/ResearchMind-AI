import { useState, useCallback, useRef } from "react";
import type { ChatMessage, Source } from "../types/chat";
import { sendChatMessage } from "../api/chat";
import { copyToClipboard } from "../utils/copyToClipboard";
import { startTypingAnimation } from "../utils/typing";

const SESSION_KEY = "ai-research-session-id";

function getSessionId(): string {
  let id = localStorage.getItem(SESSION_KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, id);
  }
  return id;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastSources, setLastSources] = useState<Source[]>([]);

  const sessionId = useRef(getSessionId());
  const abortControllerRef = useRef<AbortController | null>(null);
  const typingCancelRef = useRef<(() => void) | null>(null);

  const sendMessage = useCallback(
    async (question: string, documentId?: string | null) => {
      // Cancel any inflight request
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      // Cancel any ongoing typing animation
      if (typingCancelRef.current) {
        typingCancelRef.current();
      }

      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      setError(null);
      setIsLoading(true);

      // Add user message
      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: question,
      };

      // Add placeholder assistant message (typing state)
      const assistantId = crypto.randomUUID();
      const assistantPlaceholder: ChatMessage = {
        id: assistantId,
        role: "assistant",
        content: "",
        isTyping: true,
      };

      setMessages((prev) => [...prev, userMessage, assistantPlaceholder]);

      try {
        const data = await sendChatMessage(
          question,
          sessionId.current,
          documentId,
          abortController.signal,
        );

        setLastSources(data.sources);

        // Start typing animation for the answer
        const cancel = startTypingAnimation(
          data.answer,
          (visibleText) => {
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantId
                  ? { ...msg, content: visibleText, isTyping: true }
                  : msg,
              ),
            );
          },
          () => {
            // Animation complete — set final state
            setMessages((prev) =>
              prev.map((msg) =>
                msg.id === assistantId
                  ? {
                      ...msg,
                      content: data.answer,
                      sources: data.sources,
                      isTyping: false,
                    }
                  : msg,
              ),
            );
            setIsLoading(false);
          },
        );

        typingCancelRef.current = cancel;
      } catch (err: unknown) {
        // Don't treat abort as an error
        if (err instanceof Error && err.name === "CanceledError") return;
        if (err instanceof DOMException && err.name === "AbortError") return;

        setError("Chat failed. Please try again.");
        // Remove the placeholder assistant message
        setMessages((prev) => prev.filter((msg) => msg.id !== assistantId));
        setIsLoading(false);
      }
    },
    [],
  );

  const clearChat = useCallback(() => {
    // Cancel inflight
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    if (typingCancelRef.current) {
      typingCancelRef.current();
    }
    setMessages([]);
    setLastSources([]);
    setError(null);
    setIsLoading(false);

    // Generate new session for fresh chat
    const newId = crypto.randomUUID();
    sessionId.current = newId;
    localStorage.setItem(SESSION_KEY, newId);
  }, []);

  const regenerate = useCallback(
    (documentId?: string | null) => {
      // Find the last user message
      const lastUserMessage = [...messages]
        .reverse()
        .find((m) => m.role === "user");

      if (!lastUserMessage) return;

      // Remove the last assistant message
      setMessages((prev) => {
        const lastAssistantIndex = prev.findLastIndex(
          (m) => m.role === "assistant",
        );
        if (lastAssistantIndex === -1) return prev;
        return prev.filter((_, i) => i !== lastAssistantIndex);
      });

      // Re-send — but we need to remove the last user message too since sendMessage adds it
      setMessages((prev) => {
        const lastUserIndex = prev.findLastIndex((m) => m.role === "user");
        if (lastUserIndex === -1) return prev;
        return prev.filter((_, i) => i !== lastUserIndex);
      });

      sendMessage(lastUserMessage.content, documentId);
    },
    [messages, sendMessage],
  );

  const copyAnswer = useCallback(async (messageId: string) => {
    const msg = messages.find((m) => m.id === messageId);
    if (!msg) return false;
    return copyToClipboard(msg.content);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [messages]);

  return {
    messages,
    isLoading,
    error,
    lastSources,
    sendMessage,
    clearChat,
    regenerate,
    copyAnswer,
  };
}
