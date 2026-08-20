# 🧠 DocPilot

### AI-Powered Document Intelligence & RAG Assistant

> **Upload your documents. Ask questions. Get intelligent, context-aware answers.**

DocPilot is an AI-powered document intelligence platform that lets you upload documents and interact with them through a conversational interface.

It combines **Retrieval-Augmented Generation (RAG)**, document processing, semantic embeddings, vector search, and **Google Gemini** to provide answers grounded in your uploaded documents.

---

## ✨ Features

- 📄 **Document Upload**
  - Upload PDF documents directly through the web interface.
  - Automatic document processing and text extraction.

- 🧠 **AI-Powered Q&A**
  - Ask natural-language questions about your documents.
  - Powered by Google Gemini.

- 🔎 **RAG-Based Retrieval**
  - Relevant document chunks are retrieved before generating answers.
  - Helps keep responses grounded in the uploaded content.

- 🧩 **Semantic Search**
  - Documents are converted into embeddings.
  - FAISS is used for efficient similarity search.

- 💬 **Conversation Management**
  - Create and manage multiple conversations.
  - Continue previous conversations.
  - Delete conversations when no longer needed.

- ⚡ **Modern React Interface**
  - Clean, responsive chat experience.
  - Built with React and Vite.

- 🏗️ **Modular Backend**
  - FastAPI-based REST API.
  - Separate services for extraction, embeddings, retrieval, RAG, conversations, and document processing.

---

## 🖥️ Architecture

```text
                         ┌─────────────────────┐
                         │      React UI       │
                         │    Vite + React     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     FastAPI API     │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
                    ▼               ▼               ▼
              ┌──────────┐   ┌────────────┐   ┌────────────┐
              │   PDF    │   │ Embedding  │   │Conversation │
              │Extraction│   │  Service   │   │  Service   │
              └────┬─────┘   └─────┬──────┘   └────────────┘
                   │               │
                   ▼               ▼
              ┌──────────────────────────┐
              │       FAISS Vector       │
              │          Search          │
              └────────────┬─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ RAG Service  │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Google Gemini│
                    └──────────────┘
🛠️ Tech Stack
Frontend
React
Vite
JavaScript
CSS
Backend
Python
FastAPI
SQLAlchemy
REST API
AI / RAG
Google Gemini
Embeddings
Retrieval-Augmented Generation (RAG)
FAISS
Document Processing
PDF text extraction
Text cleaning
Chunking
Vector indexing
📁 Project Structure
DocPilot/
│
├── apps/
│   │
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   └── v1/
│   │   │   │       ├── chat/
│   │   │   │       ├── conversations/
│   │   │   │       └── documents/
│   │   │   │
│   │   │   ├── db/
│   │   │   │   └── models/
│   │   │   │
│   │   │   └── services/
│   │   │       ├── chunk_service.py
│   │   │       ├── conversation_service.py
│   │   │       ├── document_processing_service.py
│   │   │       ├── embedding_service.py
│   │   │       ├── faiss_service.py
│   │   │       ├── llm_service.py
│   │   │       ├── pdf_extraction_service.py
│   │   │       ├── rag_service.py
│   │   │       ├── retrieval_service.py
│   │   │       └── text_cleaner.py
│   │   │
│   │   ├── data/
│   │   ├── database.py
│   │   └── main.py
│   │
│   └── frontend/
│       ├── src/
│       │   ├── components/
│       │   ├── services/
│       │   ├── App.jsx
│       │   ├── App.css
│       │   └── index.css
│       │
│       ├── package.json
│       └── vite.config.js
│
└── README.md
🚀 Getting Started
1. Clone the repository
git clone https://github.com/omchaudhary360/DocPilot.git
cd DocPilot
⚙️ Backend Setup
2. Create a virtual environment

Windows:

python -m venv .venv

Activate it:

.venv\Scripts\Activate.ps1

Linux / macOS:

python -m venv .venv
source .venv/bin/activate
3. Install backend dependencies

Navigate to the backend:

cd apps/backend

Install dependencies:

pip install -r requirements.txt
4. Configure environment variables

Create a .env file inside:

apps/backend/

Add your Gemini API key:

GEMINI_API_KEY=your_gemini_api_key

⚠️ Never commit your real API key to GitHub.

5. Start the backend

From apps/backend:

uvicorn main:app --reload

The API will be available at:

http://127.0.0.1:8000
🎨 Frontend Setup

Open another terminal.

Navigate to:

cd apps/frontend

Install dependencies:

npm install

Start the development server:

npm run dev

Vite will provide the local frontend URL, typically:

http://localhost:5173
🔄 How DocPilot Works

The general document-question answering pipeline is:

PDF Upload
    │
    ▼
PDF Text Extraction
    │
    ▼
Text Cleaning
    │
    ▼
Document Chunking
    │
    ▼
Embedding Generation
    │
    ▼
FAISS Vector Index
    │
    ▼
User Question
    │
    ▼
Semantic Retrieval
    │
    ▼
Relevant Context
    │
    ▼
RAG Pipeline
    │
    ▼
Google Gemini
    │
    ▼
AI Response
🔌 API Endpoints
Chat
POST /api/v1/chat

Send a question and receive an AI-generated response based on the available document context.

Conversations
GET    /api/v1/conversations
POST   /api/v1/conversations
DELETE /api/v1/conversations/{conversation_id}
Documents
POST /api/v1/documents/upload

Upload and process a document.

🔐 Environment Variables
Variable	Description
GEMINI_API_KEY	Google Gemini API key

Keep environment files private.

Recommended:

.env

should remain in .gitignore.

🧪 Development

Run the backend:

cd apps/backend
uvicorn main:app --reload

Run the frontend:

cd apps/frontend
npm run dev
📌 Versioning
Version 1

The original release is preserved with the Git tag:

v1.0
Version 2

The current production development version is available on:

main
⚠️ Important Notes
API Quota

DocPilot uses the Google Gemini API. API usage is subject to the quota and billing limits of the Google AI project associated with your API key.

Local Data

Generated document data, uploaded PDFs, FAISS indexes, and other runtime artifacts should not be committed to the repository.

Keep runtime data under:

apps/backend/data/

and ensure it remains ignored by Git.

🛡️ Security

Before deploying DocPilot publicly:

Never expose your Gemini API key.
Store secrets in environment variables.
Do not commit .env.
Do not commit uploaded documents.
Do not expose private document data through public endpoints.
Configure appropriate CORS settings for production.
Use HTTPS in production.
🚀 Deployment

DocPilot can be deployed using a separate frontend and backend hosting setup.

Typical production architecture:

                   Internet
                       │
                       ▼
              ┌─────────────────┐
              │  Frontend Host  │
              │   React / Vite  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  Backend Host   │
              │     FastAPI     │
              └────────┬────────┘
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
        ┌───────────┐     ┌────────────┐
        │ Database  │     │ Gemini API │
        └───────────┘     └────────────┘

Production deployment should use persistent storage for uploaded documents, indexes, and database data rather than relying on temporary local filesystem storage.

💡 Why DocPilot?

Traditional document search often requires manually scanning large files.

DocPilot turns that process into a conversation.

Instead of:

Search → Open document → Find section → Read → Repeat

you can:

Upload → Ask → Understand

🌟 Future Improvements

Potential future enhancements include:

🌐 Multi-user authentication
📚 Support for more document formats
🗂️ Document collections
🔐 User-specific document isolation
☁️ Cloud object storage
⚡ Streaming AI responses
📊 Usage analytics
🧠 Improved retrieval and reranking
🌍 Production-scale deployment
👨‍💻 Author

Om Chaudhary

Built with ❤️ using React, FastAPI, FAISS, RAG, and Google Gemini.

⭐ Support

If you find DocPilot useful, consider giving the repository a ⭐ on GitHub.

DocPilot — Your documents, your questions, one intelligent conversation.