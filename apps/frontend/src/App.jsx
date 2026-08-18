import { useState } from "react";
import "./App.css";
import { uploadDocument, askQuestion } from "./services/api";

function App() {
  const [file, setFile] = useState(null);
  const [document, setDocument] = useState(null);

  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);

  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = async (event) => {
    const selectedFile = event.target.files[0];

    if (!selectedFile) {
      return;
    }

    setFile(selectedFile);
    setError("");
    setDocument(null);

    try {
      setUploading(true);

      const result = await uploadDocument(selectedFile);

      setDocument(result);
    } catch (err) {
      setError(err.message);
      setFile(null);
    } finally {
      setUploading(false);
    }
  };

  const handleAsk = async () => {
    if (!question.trim() || asking) {
      return;
    }

    const currentQuestion = question.trim();

    setQuestion("");
    setError("");

    setMessages((previous) => [
      ...previous,
      {
        type: "user",
        text: currentQuestion,
      },
    ]);

    try {
      setAsking(true);

      const result = await askQuestion(
        currentQuestion,
        document.document_id
      );

      setMessages((previous) => [
        ...previous,
        {
          type: "assistant",
          text: result.answer,
          sources: result.sources || [],
        },
      ]);
    } catch (err) {
      setError(err.message);
    } finally {
      setAsking(false);
    }
  };

  return (
    <div className="app">

      {/* Sidebar */}
      <aside className="sidebar">

        <div className="brand">
          <div className="brand-icon">✦</div>

          <div>
            <h1>DocMind</h1>
            <p>AI Document Intelligence</p>
          </div>
        </div>

        <button
          className="new-chat"
          onClick={() => setMessages([])}
        >
          + New Conversation
        </button>

        <div className="sidebar-section">

          <p className="section-title">
            WORKSPACE
          </p>

          <div className="sidebar-item active">
            <span>▣</span>
            Documents
          </div>

          <div className="sidebar-item">
            <span>◫</span>
            Conversations
          </div>

        </div>

        <div className="sidebar-bottom">

          <div className="system-status">

            <span className="status-dot"></span>

            <div>
              <strong>System Online</strong>
              <small>RAG pipeline active</small>
            </div>

          </div>

        </div>

      </aside>


      {/* Main */}
      <main className="main">

        {/* Header */}
        <header className="topbar">

          <div>
            <p className="eyebrow">
              DOCUMENT WORKSPACE
            </p>

            <h2>
              Ask your documents
            </h2>
          </div>

          <div className="topbar-status">

            <span className="status-dot"></span>

            API Connected

          </div>

        </header>


        <div className="content">

          {/* Upload */}
          <section className="upload-section">

            <div className="section-heading">

              <div>
                <p className="eyebrow">
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


            <label className="upload-box">

              <input
                type="file"
                accept=".pdf"
                onChange={handleFileChange}
                disabled={uploading}
              />

              <div className="upload-icon">
                ↑
              </div>

              <h4>
                {uploading
                  ? "Processing document..."
                  : "Upload a PDF"}
              </h4>

              <p>
                {uploading
                  ? "Extracting, chunking and indexing your document"
                  : "Drag and drop your document here or click to browse"}
              </p>

              <span className="upload-format">
                PDF files only
              </span>

            </label>


            {file && (

              <div className="document-card">

                <div className="document-icon">
                  PDF
                </div>


                <div className="document-info">

                  <strong>
                    {file.name}
                  </strong>

                  <span>
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </span>

                </div>


                {uploading ? (

                  <div className="processed">
                    Processing...
                  </div>

                ) : document ? (

                  <div className="processed">
                    <span>✓</span>
                    Processed
                  </div>

                ) : null}

              </div>

            )}


            {error && (

              <div className="error-message">
                {error}
              </div>

            )}

          </section>


          {/* Chat */}
          <section className="chat-section">

            <div className="section-heading">

              <div>

                <p className="eyebrow">
                  AI ASSISTANT
                </p>

                <h3>
                  Conversation
                </h3>

              </div>

            </div>


            <div className="chat-window">

              {messages.length === 0 ? (

                <div className="empty-chat">

                  <div className="ai-orb">
                    ✦
                  </div>

                  <h3>
                    Ask anything about your documents
                  </h3>

                  <p>
                    Upload a document and ask questions
                    in natural language. Answers are
                    grounded in your documents.
                  </p>


                  <div className="suggestions">

                    <button
                      onClick={() =>
                        setQuestion(
                          "What is the objective of this project?"
                        )
                      }
                    >
                      What is the objective?
                    </button>


                    <button
                      onClick={() =>
                        setQuestion(
                          "Summarize this document"
                        )
                      }
                    >
                      Summarize the document
                    </button>


                    <button
                      onClick={() =>
                        setQuestion(
                          "What are the key points?"
                        )
                      }
                    >
                      Key points
                    </button>

                  </div>

                </div>

              ) : (

                <div className="messages">

                  {messages.map(
                    (message, index) => (

                      <div
                        className={`message ${message.type}`}
                        key={index}
                      >

                        <div>
                          {message.text}
                        </div>


                        {message.type ===
                          "assistant" &&
                          message.sources?.length >
                            0 && (

                            <div className="sources">

                              <div className="sources-title">
                                Sources
                              </div>

                              {message.sources.map(
                                (source, sourceIndex) => (

                                  <div
                                    className="source-card"
                                    key={sourceIndex}
                                  >

                                    <span>
                                      📄
                                    </span>

                                    <div>

                                      <strong>
                                        {source.document}
                                      </strong>

                                      <small>
                                        Page{" "}
                                        {source.page}
                                        {" • "}
                                        Chunk{" "}
                                        {source.chunk_id}
                                      </small>

                                    </div>

                                  </div>

                                )
                              )}

                            </div>

                          )}

                      </div>

                    )
                  )}


                  {asking && (

                    <div className="message assistant">
                      Thinking...
                    </div>

                  )}

                </div>

              )}

            </div>


            {/* Input */}
            <div className="chat-input-wrapper">

              <input
                type="text"
                placeholder={
                  document
                    ? "Ask a question about your document..."
                    : "Upload a document first..."
                }
                value={question}
                disabled={asking}
                onChange={(event) =>
                  setQuestion(event.target.value)
                }
                onKeyDown={(event) => {

                  if (
                    event.key === "Enter"
                  ) {
                    handleAsk();
                  }

                }}
              />


              <button
                className="send-button"
                onClick={handleAsk}
                disabled={
                  asking ||
                  !question.trim()
                }
              >
                ↑
              </button>

            </div>


            <p className="disclaimer">
              AI responses are generated from
              your uploaded documents.
            </p>

          </section>

        </div>

      </main>

    </div>
  );
}

export default App;