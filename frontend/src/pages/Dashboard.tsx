import { motion } from "framer-motion";
import Header from "../components/Layout/Header";
import Sidebar from "../components/Layout/Sidebar";
import ChatBox from "../components/Chat/ChatBox";
import ChatInput from "../components/Chat/ChatInput";
import SourcePanel from "../components/Chat/SourcePanel";
import { useDocuments } from "../hooks/useDocuments";
import { useChat } from "../hooks/useChat";
import { updateConversationDocuments } from "../api/conversations";

export default function Dashboard() {
  const {
    documents,
    isLoading: docsLoading,
    error: docsError,
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
  } = useDocuments();

  const {
    messages,
    isLoading: chatLoading,
    error: chatError,
    lastSources,
    conversations,
    currentConversationId,
    sendMessage,
    clearChat,
    regenerate,
    copyAnswer,
    selectConversation,
    removeConversation,
    editConversationTitle,
    clearAllConversationsHistory,
  } = useChat();

  const scopedDocuments = documents
    .filter((d) => selectedDocumentIds.includes(d.document_id))
    .map((d) => ({ id: d.document_id, name: d.filename }));

  const headerLabel =
    selectedDocumentIds.length === 1
      ? scopedDocuments[0]?.name ?? null
      : selectedDocumentIds.length > 1
      ? `${selectedDocumentIds.length} documents scoped`
      : null;

  const handleToggleDocument = (id: string) => {
    toggleDocument(id);
    if (currentConversationId) {
      const next = selectedDocumentIds.includes(id)
        ? selectedDocumentIds.filter((d) => d !== id)
        : [...selectedDocumentIds, id];
      updateConversationDocuments(currentConversationId, next).catch(() => {});
    }
  };

  const handleClearScope = () => {
    clearSelection();
    if (currentConversationId) {
      updateConversationDocuments(currentConversationId, []).catch(() => {});
    }
  };

  const handleSelectConversation = async (id: number | null) => {
    const docIds = await selectConversation(id);
    setSelectedDocumentIds(docIds);
  };

  function handleSendMessage(text: string) {
    sendMessage(text, selectedDocumentIds);
  }

  function handleRegenerate() {
    regenerate(selectedDocumentIds);
  }

  function handleSendExample(prompt: string) {
    sendMessage(prompt, selectedDocumentIds);
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
      className="flex flex-col h-screen w-screen overflow-hidden bg-bg"
    >
      <Header selectedDocumentName={headerLabel} />

      <div className="flex flex-1 min-h-0">
        {/* Left — Research Library & Conversations */}
        <div className="w-64 shrink-0">
          <Sidebar
            documents={documents}
            isLoading={docsLoading}
            error={docsError}
            selectedDocumentIds={selectedDocumentIds}
            onToggleDocument={handleToggleDocument}
            onClearDocumentSelection={handleClearScope}
            isUploading={isUploading}
            uploadProgress={uploadProgress}
            uploadError={uploadError}
            onUpload={upload}
            onDelete={remove}
            onRetryFetch={fetchDocs}
            
            conversations={conversations}
            currentConversationId={currentConversationId}
            onSelectConversation={handleSelectConversation}
            onDeleteConversation={removeConversation}
            onRenameConversation={editConversationTitle}
            onClearAllDocuments={clearAllDocs}
            onClearAllConversations={clearAllConversationsHistory}
          />
        </div>

        {/* Center — Chat */}
        <div className="flex-1 flex flex-col min-w-0 border-x border-border">
          <ChatBox
            messages={messages}
            isLoading={chatLoading}
            error={chatError}
            onCopy={copyAnswer}
            onRegenerate={handleRegenerate}
            onClearChat={clearChat}
            onSendExample={handleSendExample}
            documents={documents}
            hasConversations={conversations.length > 0}
            onUpload={upload}
            onSelectDocument={selectDocument}
          />
          <ChatInput
            isLoading={chatLoading}
            scopedDocuments={scopedDocuments}
            onRemoveScopedDocument={handleToggleDocument}
            onClearScope={handleClearScope}
            onSend={handleSendMessage}
          />
        </div>

        {/* Right — Sources */}
        <div className="w-64 shrink-0">
          <SourcePanel sources={lastSources} />
        </div>
      </div>
    </motion.div>
  );
}
