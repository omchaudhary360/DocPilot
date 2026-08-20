import { useEffect, useRef, useState } from "react";
import "./App.css";

import Logo from "./components/Logo";

import {
  uploadDocument,
  createConversation,
  getConversations,
  getConversation,
  deleteConversation,
  askQuestion,
} from "./services/api";


function App() {

  // =========================================
  // DOCUMENT
  // =========================================

  const [document, setDocument] = useState(null);


  // =========================================
  // CONVERSATIONS
  // =========================================

  const [conversationId, setConversationId] =
    useState(null);

  const [conversations, setConversations] =
    useState([]);


  // =========================================
  // CHAT
  // =========================================

  const [messages, setMessages] =
    useState([]);

  const [question, setQuestion] =
    useState("");


  // =========================================
  // UI
  // =========================================

  const [activeView, setActiveView] =
    useState("documents");

  const [uploading, setUploading] =
    useState(false);

  const [asking, setAsking] =
    useState(false);

  const [error, setError] =
    useState("");


  // =========================================
  // REFS
  // =========================================

  const messagesEndRef =
    useRef(null);

  const inputRef =
    useRef(null);


  // =========================================
  // LOAD CONVERSATIONS
  // =========================================

  useEffect(() => {
    loadConversations();
  }, []);


  async function loadConversations() {

    try {

      const data =
        await getConversations();

      setConversations(
        Array.isArray(data)
          ? data
          : []
      );

    } catch (err) {

      console.error(
        "Failed to load conversations:",
        err
      );

    }
  }


  // =========================================
  // AUTO SCROLL
  // =========================================

  useEffect(() => {

    const timer =
      setTimeout(() => {

        messagesEndRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "end",
        });

      }, 50);

    return () => clearTimeout(timer);

  }, [messages, asking]);


  // =========================================
  // FOCUS INPUT
  // =========================================

  useEffect(() => {

    if (
      document &&
      conversationId &&
      activeView === "documents"
    ) {

      inputRef.current?.focus();

    }

  }, [
    document,
    conversationId,
    activeView,
  ]);


  // =========================================
  // UPLOAD DOCUMENT
  // =========================================

  async function handleFileChange(event) {

    const file =
      event.target.files?.[0];

    if (!file) return;


    if (
      file.type !== "application/pdf"
    ) {

      setError(
        "Please upload a PDF file."
      );

      return;
    }


    setError("");
    setUploading(true);


    try {

      const result =
        await uploadDocument(file);


      const documentId =
        result.document_id ||
        result.id;


      if (!documentId) {

        throw new Error(
          "Document ID was not returned by the server."
        );

      }


      const uploadedDocument = {

        id: documentId,

        name:
          result.file_name ||
          result.original_name ||
          file.name,

        size: file.size,

        status:
          result.status ||
          "processed",

      };


      setDocument(
        uploadedDocument
      );


      // =====================================
      // CREATE FRESH CONVERSATION
      // =====================================

      const conversation =
        await createConversation(
          "New Conversation",
          documentId
        );


      setConversationId(
        conversation.id
      );


      setMessages([]);
      setQuestion("");


      await loadConversations();


      setActiveView(
        "documents"
      );


    } catch (err) {

      console.error(err);

      setError(
        err.message ||
        "Document upload failed."
      );

    } finally {

      setUploading(false);

      event.target.value = "";

    }
  }


  // =========================================
  // NEW CONVERSATION
  // =========================================

  async function handleNewConversation() {

    setError("");

    setMessages([]);

    setQuestion("");


    if (!document) {

      setConversationId(null);

      setActiveView(
        "documents"
      );

      return;
    }


    try {

      const conversation =
        await createConversation(
          "New Conversation",
          document.id
        );


      setConversationId(
        conversation.id
      );


      await loadConversations();


      setActiveView(
        "documents"
      );


      // Focus input immediately
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);


    } catch (err) {

      console.error(err);

      setError(
        err.message ||
        "Could not create a new conversation."
      );

    }
  }


  // =========================================
  // OPEN CONVERSATION
  // =========================================

  async function openConversation(
    conversation
  ) {

    try {

      setError("");

      setAsking(false);


      const fullConversation =
        await getConversation(
          conversation.id
        );


      setConversationId(
        fullConversation.id
      );


      // =====================================
      // RESTORE MESSAGES
      // =====================================

      const restoredMessages =
        (
          fullConversation.messages ||
          []
        ).map((message) => ({

          id:
            message.id,

          role:
            message.role,

          content:
            message.content,

          sources:
            message.sources || [],

        }));


      setMessages(
        restoredMessages
      );


      // =====================================
      // RESTORE DOCUMENT
      // =====================================

      if (
        fullConversation.document_id
      ) {

        setDocument({

          id:
            fullConversation.document_id,

          name:
            fullConversation.document_name ||
            conversation.document_name ||
            "Document",

          size: 0,

          status:
            "processed",

        });

      }


      setQuestion("");

      setActiveView(
        "documents"
      );


    } catch (err) {

      console.error(err);

      setError(
        err.message ||
        "Could not open conversation."
      );

    }
  }


  // =========================================
  // ASK QUESTION
  // =========================================

  async function handleAsk(
    customQuestion = null
  ) {

    const text =
      (
        customQuestion ??
        question
      ).trim();


    if (!text) return;


    if (!document) {

      setError(
        "Please upload a document first."
      );

      return;
    }


    if (!conversationId) {

      setError(
        "Please start a conversation first."
      );

      return;
    }


    if (asking) return;


    setError("");


    // =====================================
    // CLEAR INPUT IMMEDIATELY
    // =====================================

    setQuestion("");


    // =====================================
    // ADD USER MESSAGE ONCE
    // =====================================

    const userMessage = {

      id:
        `user-${Date.now()}-${Math.random()}`,

      role:
        "user",

      content:
        text,

      sources:
        [],

    };


    setMessages(
      (previous) => [
        ...previous,
        userMessage,
      ]
    );


    setAsking(true);


    try {

      const result =
        await askQuestion(
          text,
          document.id,
          conversationId,
          3
        );


      // ===================================
      // ASSISTANT MESSAGE
      // ===================================

      const assistantMessage = {

        id:
          `assistant-${Date.now()}-${Math.random()}`,

        role:
          "assistant",

        content:
          result.answer ||
          "I could not generate an answer.",

        sources:
          result.sources || [],

      };


      setMessages(
        (previous) => [
          ...previous,
          assistantMessage,
        ]
      );


      // ===================================
      // UPDATE CONVERSATION LIST
      // ===================================

      await loadConversations();


    } catch (err) {

      console.error(err);


      setError(
        err.message ||
        "Failed to get an answer."
      );


      // ===================================
      // ERROR MESSAGE
      // ===================================

      setMessages(
        (previous) => [

          ...previous,

          {
            id:
              `error-${Date.now()}`,

            role:
              "assistant",

            content:
              "I couldn't process that question. Please try again.",

            sources:
              [],

            isError:
              true,
          },

        ]
      );


    } finally {

      setAsking(false);

      // Keep input ready
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);

    }
  }


  // =========================================
  // ENTER TO SEND
  // =========================================

  function handleKeyDown(event) {

    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {

      event.preventDefault();

      if (
        !asking &&
        question.trim()
      ) {

        handleAsk();

      }

    }

  }


  // =========================================
  // DELETE CONVERSATION
  // =========================================

  async function handleDeleteConversation(
    event,
    id
  ) {

    event.stopPropagation();


    try {

      await deleteConversation(id);


      setConversations(
        (previous) =>
          previous.filter(
            (item) =>
              item.id !== id
          )
      );


      if (
        conversationId === id
      ) {

        setConversationId(null);

        setMessages([]);

        setQuestion("");

      }


    } catch (err) {

      console.error(err);

      setError(
        err.message ||
        "Could not delete conversation."
      );

    }
  }


  // =========================================
  // FILE SIZE
  // =========================================

  function formatFileSize(bytes) {

    if (!bytes) return "";

    if (
      bytes < 1024 * 1024
    ) {

      return `${Math.round(
        bytes / 1024
      )} KB`;

    }

    return `${(
      bytes /
      (1024 * 1024)
    ).toFixed(2)} MB`;

  }


  // =========================================
  // SUGGESTIONS
  // =========================================

  const suggestions = [

    "Summarize this document",

    "What are the key points?",

    "Explain this document",

  ];


  // =========================================
  // RENDER
  // =========================================

  return (

    <div className="app">


      {/* =====================================
          SIDEBAR
      ===================================== */}

      <aside className="sidebar">

        <div>

          <div className="brand">

            <Logo
              size={42}
              showText={true}
              dark={true}
            />

          </div>


          <button
            className="new-chat"
            onClick={
              handleNewConversation
            }
          >

            <span>＋</span>

            New Conversation

          </button>


          <div className="sidebar-section">

            <div className="section-title">
              WORKSPACE
            </div>


            <button
              className={`sidebar-item ${
                activeView === "documents"
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                setActiveView(
                  "documents"
                )
              }
            >

              <span>▣</span>

              Documents

            </button>


            <button
              className={`sidebar-item ${
                activeView === "conversations"
                  ? "active"
                  : ""
              }`}
              onClick={() =>
                setActiveView(
                  "conversations"
                )
              }
            >

              <span>◫</span>

              Conversations

              {conversations.length > 0 && (

                <span className="conversation-badge">

                  {conversations.length}

                </span>

              )}

            </button>

          </div>

        </div>


        <div className="sidebar-bottom">

          <div className="system-status">

            <span className="status-dot" />

            <div>

              <strong>
                System Online
              </strong>

              <small>
                RAG pipeline active
              </small>

            </div>

          </div>

        </div>

      </aside>


      {/* =====================================
          MAIN
      ===================================== */}

      <main className="main">


        <header className="topbar">

          <div>

            <p className="eyebrow">
              DOCUMENT WORKSPACE
            </p>

            <h2>

              {activeView === "documents"
                ? "Ask your documents"
                : "Your conversations"}

            </h2>

          </div>


          <div className="topbar-status">

            <span className="status-dot" />

            API Connected

          </div>

        </header>


        {/* =====================================
            DOCUMENT WORKSPACE
        ===================================== */}

        {activeView === "documents" && (

          <div className="content">


            {/* =================================
                DOCUMENT
            ================================= */}

            <section className="upload-section">

              <div className="section-heading">

                <div>

                  <p className="section-title-light">
                    KNOWLEDGE BASE
                  </p>

                  <h3>
                    Your Documents
                  </h3>

                </div>


                <span className="document-count">

                  {document
                    ? "1 document"
                    : "0 documents"}

                </span>

              </div>


              {!document && (

                <label className="upload-box">

                  <input
                    type="file"
                    accept="application/pdf"
                    onChange={
                      handleFileChange
                    }
                    disabled={
                      uploading
                    }
                  />


                  <div className="upload-icon">

                    {uploading
                      ? "..."
                      : "↑"}

                  </div>


                  <h4>

                    {uploading
                      ? "Processing document..."
                      : "Upload a PDF"}

                  </h4>


                  <p>

                    {uploading
                      ? "Preparing your document for AI analysis"
                      : "Drag and drop your document here or click to browse"}

                  </p>


                  <span className="upload-format">
                    PDF files only
                  </span>

                </label>

              )}


              {document && (

                <div className="document-card">

                  <div className="document-icon">
                    PDF
                  </div>


                  <div className="document-info">

                    <strong>
                      {document.name}
                    </strong>

                    <span>

                      {formatFileSize(
                        document.size
                      )}

                    </span>

                  </div>


                  <div className="processed">
                    ✓ Ready to chat
                  </div>

                </div>

              )}


              {document && (

                <label className="change-document">

                  <input
                    type="file"
                    accept="application/pdf"
                    onChange={
                      handleFileChange
                    }
                  />

                  + Upload another document

                </label>

              )}


              {error && (

                <div className="error-message">
                  {error}
                </div>

              )}

            </section>


            {/* =================================
                CHAT
            ================================= */}

            <section className="chat-section">

              <div className="chat-header">

                <div>

                  <p className="section-title-light">
                    AI ASSISTANT
                  </p>

                  <h3>
                    Conversation
                  </h3>

                </div>


                {conversationId && (

                  <span className="conversation-id">
                    Conversation #{conversationId}
                  </span>

                )}

              </div>


              <div
                className={`chat-window ${
                  messages.length
                    ? "has-messages"
                    : ""
                }`}
              >


                {/* =================================
                    EMPTY STATE
                ================================= */}

                {messages.length === 0 && (

                  <div className="empty-chat">

                    <div className="ai-orb">

                      <Logo
                        size={38}
                        showText={false}
                        dark={false}
                      />

                    </div>


                    <h3>
                      Ask anything about your documents
                    </h3>


                    <p>

                      {document
                        ? "Your document is ready. Ask a question and DocPilot will find the relevant information."
                        : "Upload a document and ask questions in natural language. Answers are grounded in your documents."}

                    </p>


                    <div className="suggestions">

                      {suggestions.map(
                        (suggestion) => (

                          <button
                            key={suggestion}
                            onClick={() =>
                              handleAsk(
                                suggestion
                              )
                            }
                            disabled={
                              !document ||
                              !conversationId ||
                              asking
                            }
                          >

                            {suggestion}

                          </button>

                        )
                      )}

                    </div>

                  </div>

                )}


                {/* =================================
                    MESSAGES
                ================================= */}

                {messages.length > 0 && (

                  <div className="messages">

                    {messages.map(
                      (message) => (

                        <div
                          key={message.id}
                          className={`message-row ${
                            message.role
                          }`}
                        >


                          {message.role ===
                            "assistant" && (

                            <div className="message-avatar">

                              <Logo
                                size={27}
                                showText={false}
                                dark={false}
                              />

                            </div>

                          )}


                          <div
                            className={`message ${
                              message.role
                            } ${
                              message.isError
                                ? "message-error"
                                : ""
                            }`}
                          >

                            <div className="message-content">
                              {message.content}
                            </div>


                            {message.role ===
                              "assistant" &&
                              message.sources?.length >
                                0 && (

                                <div className="sources">

                                  <div className="sources-title">
                                    Sources
                                  </div>


                                  {message.sources.map(
                                    (
                                      source,
                                      index
                                    ) => (

                                      <div
                                        className="source-card"
                                        key={`${source.chunk_id}-${index}`}
                                      >

                                        <div className="document-icon">
                                          PDF
                                        </div>


                                        <div>

                                          <strong>
                                            {
                                              source.document
                                            }
                                          </strong>

                                          <small>
                                            Page{" "}
                                            {
                                              source.page
                                            }
                                          </small>

                                        </div>

                                      </div>

                                    )
                                  )}

                                </div>

                              )}

                          </div>

                        </div>

                      )
                    )}


                    {/* =================================
                        THINKING
                    ================================= */}

                    {asking && (

                      <div className="message-row assistant">

                        <div className="message-avatar">

                          <Logo
                            size={27}
                            showText={false}
                            dark={false}
                          />

                        </div>


                        <div className="message assistant thinking">

                          <span />
                          <span />
                          <span />

                        </div>

                      </div>

                    )}


                    <div
                      ref={messagesEndRef}
                    />

                  </div>

                )}

              </div>


              {/* =================================
                  FIXED CHAT INPUT
              ================================= */}

              <div className="chat-input-wrapper">

                <input
                  ref={inputRef}
                  value={question}
                  onChange={(event) =>
                    setQuestion(
                      event.target.value
                    )
                  }
                  onKeyDown={
                    handleKeyDown
                  }
                  placeholder={
                    document
                      ? "Ask anything about this document..."
                      : "Upload a document to start asking questions..."
                  }
                  disabled={
                    !document ||
                    !conversationId ||
                    asking
                  }
                />


                <button
                  className="send-button"
                  onClick={() =>
                    handleAsk()
                  }
                  disabled={
                    !document ||
                    !conversationId ||
                    !question.trim() ||
                    asking
                  }
                  aria-label="Send message"
                >

                  {asking
                    ? "..."
                    : "↑"}

                </button>

              </div>


              <p className="disclaimer">
                Enter to send • AI responses are grounded in your documents
              </p>

            </section>

          </div>

        )}


        {/* =====================================
            CONVERSATIONS
        ===================================== */}

        {activeView === "conversations" && (

          <div className="content">

            <div className="section-heading">

              <div>

                <p className="section-title-light">
                  HISTORY
                </p>

                <h3>
                  Recent conversations
                </h3>

              </div>


              <button
                className="new-chat-page"
                onClick={
                  handleNewConversation
                }
              >
                ＋ New Conversation
              </button>

            </div>


            {conversations.length === 0 ? (

              <div className="empty-history">

                <div>
                  ◫
                </div>

                <h3>
                  No conversations yet
                </h3>

                <p>
                  Start a conversation by
                  uploading a document.
                </p>

                <button
                  onClick={() =>
                    setActiveView(
                      "documents"
                    )
                  }
                >
                  Go to Documents
                </button>

              </div>

            ) : (

              <div className="conversation-list">

                {conversations.map(
                  (conversation) => (

                    <div
                      key={conversation.id}
                      className="conversation-card"
                      onClick={() =>
                        openConversation(
                          conversation
                        )
                      }
                    >

                      <div className="conversation-icon">
                        ◫
                      </div>


                      <div className="conversation-info">

                        <strong>
                          {conversation.title ||
                            "Untitled Conversation"}
                        </strong>

                        <span>
                          {conversation.document_name ||
                            "Document"}
                        </span>

                      </div>


                      <button
                        className="delete-conversation"
                        onClick={(event) =>
                          handleDeleteConversation(
                            event,
                            conversation.id
                          )
                        }
                        aria-label="Delete conversation"
                      >
                        ×
                      </button>


                      <span className="conversation-arrow">
                        →
                      </span>

                    </div>

                  )
                )}

              </div>

            )}

          </div>

        )}

      </main>

    </div>
  );
}


export default App;