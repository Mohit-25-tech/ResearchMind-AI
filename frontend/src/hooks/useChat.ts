import { useState, useCallback, useRef, useEffect } from "react";
import type { ChatMessage, Source } from "../types/chat";
import { sendChatMessage } from "../api/chat";
import { fetchConversations, fetchConversationMessages, deleteConversation, renameConversation, clearConversations } from "../api/conversations";
import type { Conversation } from "../api/conversations";
import { copyToClipboard } from "../utils/copyToClipboard";
import { startTypingAnimation } from "../utils/typing";

export function useChat() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastSources, setLastSources] = useState<Source[]>([]);

  const abortControllerRef = useRef<AbortController | null>(null);
  const typingCancelRef = useRef<(() => void) | null>(null);

  const loadConversations = useCallback(async () => {
    try {
      const list = await fetchConversations();
      setConversations(list);
    } catch (err) {
      console.error("Failed to load conversations:", err);
    }
  }, []);

  // Fetch list on mount
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  const selectConversation = useCallback(async (id: number | null) => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    if (typingCancelRef.current) {
      typingCancelRef.current();
    }
    
    setCurrentConversationId(id);
    setLastSources([]);
    setError(null);
    setIsLoading(false);

    if (id === null) {
      setMessages([]);
      return;
    }

    setIsLoading(true);
    try {
      const data = await fetchConversationMessages(id);
      const mappedMessages: ChatMessage[] = data.messages.map((m, idx) => ({
        id: `msg-${idx}`,
        role: m.role,
        content: m.content,
      }));
      setMessages(mappedMessages);
    } catch {
      setError("Failed to load messages.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  const removeConversation = useCallback(async (id: number) => {
    try {
      await deleteConversation(id);
      if (currentConversationId === id) {
        selectConversation(null);
      }
      loadConversations();
    } catch {
      setError("Failed to delete conversation.");
    }
  }, [currentConversationId, selectConversation, loadConversations]);

  const editConversationTitle = useCallback(async (id: number, newTitle: string) => {
    setConversations((prev) =>
      prev.map((c) => (c.id === id ? { ...c, title: newTitle } : c))
    );
    try {
      await renameConversation(id, newTitle);
      loadConversations();
    } catch {
      setError("Failed to rename conversation.");
    }
  }, [loadConversations]);

  const clearAllConversationsHistory = useCallback(async () => {
    try {
      await clearConversations();
      selectConversation(null);
      await loadConversations();
    } catch {
      setError("Failed to clear conversations history.");
    }
  }, [selectConversation, loadConversations]);

  const sendMessage = useCallback(
    async (question: string, documentId?: string | null) => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (typingCancelRef.current) {
        typingCancelRef.current();
      }

      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      setError(null);
      setIsLoading(true);

      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: "user",
        content: question,
      };

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
          currentConversationId ? String(currentConversationId) : "",
          documentId,
          abortController.signal,
        );

        setLastSources(data.sources);

        const newId = parseInt(data.session_id);
        if (!currentConversationId && newId) {
          setCurrentConversationId(newId);
        }

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
            loadConversations();
          },
        );

        typingCancelRef.current = cancel;
      } catch (err: unknown) {
        if (err instanceof Error && err.name === "CanceledError") return;
        if (err instanceof DOMException && err.name === "AbortError") return;

        setError("Chat failed. Please try again.");
        setMessages((prev) => prev.filter((msg) => msg.id !== assistantId));
        setIsLoading(false);
      }
    },
    [currentConversationId, loadConversations],
  );

  const clearChat = useCallback(() => {
    if (abortControllerRef.current) abortControllerRef.current.abort();
    if (typingCancelRef.current) typingCancelRef.current();
    setMessages([]);
    setLastSources([]);
    setError(null);
    setIsLoading(false);
    setCurrentConversationId(null);
  }, []);

  const regenerate = useCallback(
    (documentId?: string | null) => {
      const lastUserMessage = [...messages]
        .reverse()
        .find((m) => m.role === "user");

      if (!lastUserMessage) return;

      setMessages((prev) => {
        const lastAssistantIndex = prev.findLastIndex(
          (m) => m.role === "assistant",
        );
        if (lastAssistantIndex === -1) return prev;
        return prev.filter((_, i) => i !== lastAssistantIndex);
      });

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
  }, [messages]);

  return {
    messages,
    isLoading,
    error,
    lastSources,
    conversations,
    currentConversationId,
    sendMessage,
    clearChat,
    regenerate,
    copyAnswer,
    selectConversation,
    removeConversation,
    loadConversations,
    editConversationTitle,
    clearAllConversationsHistory,
  };
}
