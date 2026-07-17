import { motion } from "framer-motion";
import Header from "../components/Layout/Header";
import Sidebar from "../components/Layout/Sidebar";
import ChatBox from "../components/Chat/ChatBox";
import ChatInput from "../components/Chat/ChatInput";
import SourcePanel from "../components/Chat/SourcePanel";
import { useDocuments } from "../hooks/useDocuments";
import { useChat } from "../hooks/useChat";

export default function Dashboard() {
  const {
    documents,
    isLoading: docsLoading,
    error: docsError,
    selectedDocumentId,
    selectDocument,
    upload,
    remove,
    fetchDocs,
    isUploading,
    uploadProgress,
    uploadError,
  } = useDocuments();

  const {
    messages,
    isLoading: chatLoading,
    error: chatError,
    lastSources,
    sendMessage,
    clearChat,
    regenerate,
    copyAnswer,
  } = useChat();

  const selectedDoc = documents.find(
    (d) => d.document_id === selectedDocumentId,
  );
  const selectedDocName = selectedDoc?.filename ?? null;

  function handleSendMessage(text: string) {
    sendMessage(text, selectedDocumentId);
  }

  function handleRegenerate() {
    regenerate(selectedDocumentId);
  }

  function handleSendExample(prompt: string) {
    sendMessage(prompt, selectedDocumentId);
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
      className="flex flex-col h-screen w-screen overflow-hidden bg-bg"
    >
      <Header selectedDocumentName={selectedDocName} />

      <div className="flex flex-1 min-h-0">
        {/* Left — Research Library */}
        <div className="w-64 shrink-0">
          <Sidebar
            documents={documents}
            isLoading={docsLoading}
            error={docsError}
            selectedDocumentId={selectedDocumentId}
            isUploading={isUploading}
            uploadProgress={uploadProgress}
            uploadError={uploadError}
            onUpload={upload}
            onSelect={selectDocument}
            onDelete={remove}
            onRetryFetch={fetchDocs}
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
          />
          <ChatInput
            isLoading={chatLoading}
            selectedDocumentName={selectedDocName}
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
