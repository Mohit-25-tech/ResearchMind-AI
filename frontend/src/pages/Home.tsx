import Header from "../components/Layout/Header";
import Sidebar from "../components/Layout/Sidebar";
import ChatBox from "../components/Chat/ChatBox";
import ChatInput from "../components/Chat/ChatInput";
import SourcePanel from "../components/Chat/SourcePanel";
import { useDocuments } from "../hooks/useDocuments";
import { useChat } from "../hooks/useChat";

export default function Home() {
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

  // Find selected document name for placeholder text
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
    <div className="flex flex-col h-screen w-screen overflow-hidden">
      {/* Header */}
      <Header />

      {/* Main 3-column layout */}
      <div className="flex flex-1 min-h-0">
        {/* Left Sidebar — Documents */}
        <div className="w-72 shrink-0">
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
        <div className="flex-1 flex flex-col min-w-0 bg-bg">
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

        {/* Right Sidebar — Sources */}
        <div className="w-72 shrink-0">
          <SourcePanel sources={lastSources} />
        </div>
      </div>
    </div>
  );
}