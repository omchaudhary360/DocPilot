🚀 DocPilot
Your AI Copilot for Documents

Upload a document. Ask a question. Get an answer grounded in the document — with the source behind it.

Every organization works with documents — academic reports, policies, contracts, financial documents, applications, manuals and more.

The problem isn't always creating these documents.

The problem is finding the right information inside them.

A person may have to open a long PDF, search through multiple sections, understand the context, and still verify whether the answer is actually correct.

DocPilot is built to reduce that effort.

Instead of asking a general-purpose AI to simply "know" the answer, DocPilot first looks inside the user's uploaded document, finds the most relevant sections, and then asks the AI to answer using that retrieved information.

In simple terms:

Document
   ↓
Understand
   ↓
Find relevant information
   ↓
Generate an answer
   ↓
Show the sources
🎯 Why DocPilot?

Imagine you upload your semester result PDF.

Instead of manually searching through it for:

"What is my CGPA?"

you simply ask DocPilot.

DocPilot finds the relevant section and responds:

Your CGPA is 8.31.

But the important part is that it doesn't stop there.

It also tells you where that information came from.

For example:

Answer:
Your CGPA is 8.31.


Source:
result 6th sem.pdf
Page 1
Relevant Chunk

This makes the system more useful for situations where trust and traceability matter.

🧩 The Problem

Traditional document search usually depends on keywords.

For example, if you search for:

"employee leave"

the system may look for those exact words.

But real questions aren't always written the same way.

A user might ask:

"How many days of paid leave can an employee take?"

while the document might contain:

"Employees are entitled to 18 days of annual paid time off."

The words are different, but the meaning is similar.

DocPilot therefore uses semantic search to understand the meaning behind the question and locate relevant sections of the document.

💡 How DocPilot Solves It

DocPilot combines document processing, semantic search and Generative AI into one pipeline.

1. Upload

The user uploads a PDF through the web interface.

2. Extract

DocPilot extracts the text from the document.

For scanned/image-based documents, OCR can be used to make the content searchable.

3. Clean & Split

Large documents are cleaned and divided into smaller chunks.

Why?

Because sending an entire large document to an AI model every time would be inefficient and could overwhelm the model with irrelevant information.

4. Understand

Each chunk is converted into a numerical representation called an embedding.

This representation captures the semantic meaning of the text.

5. Store

The embeddings are stored in a FAISS vector index for fast similarity search.

6. Ask

The user asks a question in natural language.

7. Retrieve

DocPilot converts the question into an embedding and searches for the most semantically relevant chunks.

8. Generate

Those retrieved chunks are provided as context to the LLM.

The model generates an answer based on that context.

9. Cite

DocPilot returns the answer along with information about the source document, page and retrieved chunks.

🧠 What is RAG?

RAG stands for Retrieval-Augmented Generation.

The idea is simple.

Instead of:

User Question
      ↓
      AI
      ↓
  Answer

DocPilot uses:

User Question
      ↓
Semantic Search
      ↓
Relevant Document Chunks
      ↓
      AI
      ↓
Grounded Answer
      ↓
Source Information

This is important because the AI doesn't have to rely only on its general knowledge.

It gets relevant information from the user's own documents before generating the answer.

⭐ What Makes DocPilot Different?

DocPilot is designed around one principle:

The answer should be connected to the user's information.

🔹 Not just a chatbot

A general chatbot is designed to answer broad questions.

DocPilot focuses on questions about specific documents.

🔹 Not just keyword search

Traditional search looks primarily for matching words.

DocPilot uses semantic similarity, allowing it to find relevant information even when the wording of the question and document is different.

🔹 Not just document extraction

Extracting text from a PDF isn't enough.

DocPilot takes the extracted information through an entire pipeline:

Extraction
   ↓
Cleaning
   ↓
Chunking
   ↓
Embedding
   ↓
Vector Search
   ↓
Retrieval
   ↓
LLM
   ↓
Answer + Sources
🔹 Source-aware answers

DocPilot doesn't only return an answer.

It also exposes the retrieved source information so the user can understand where the answer came from.

🔹 Document-aware retrieval

When a user is working with a particular uploaded document, retrieval can be restricted to that document rather than blindly mixing results from unrelated documents.

This becomes especially important when multiple documents are present in the system.

🌍 Real-World Use Cases

DocPilot is designed to be useful across different document-heavy environments.

🏢 HR

Upload:

Employee policies
HR manuals
Leave policies
Employment documents

Ask:

"How many days of leave are available?"

🏦 Banking & Finance

Upload:

Loan applications
Financial documents
Policy documents

Ask:

"What information is required for this application?"

🎓 Education

Upload:

Results
Project reports
Course documents
Academic regulations

Ask:

"What is the student's CGPA?"

or:

"What are the objectives of this project?"

⚖️ Legal & Compliance

Upload:

Agreements
Policies
Compliance documents

Ask:

"What are the obligations mentioned in this section?"

🏢 Enterprise Knowledge

Organizations often have information spread across hundreds or thousands of internal documents.

Instead of manually searching through them, employees could interact with the organization's knowledge through natural-language questions.

🏗️ System Architecture

At a high level, DocPilot consists of four major layers:

                    ┌──────────────────────┐
                    │      User            │
                    │  Upload / Question   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    React Frontend    │
                    │      DocPilot UI      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │     FastAPI Backend  │
                    │     REST API Layer   │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
       ┌──────────────────┐       ┌──────────────────┐
       │ Document         │       │ Question         │
       │ Processing       │       │ Processing       │
       └────────┬─────────┘       └────────┬─────────┘
                │                          │
                ▼                          ▼
       ┌──────────────────┐       ┌──────────────────┐
       │ Text Extraction  │       │ Query Embedding  │
       │ + OCR            │       └────────┬─────────┘
       └────────┬─────────┘                │
                ▼                          ▼
       ┌──────────────────┐       ┌──────────────────┐
       │ Chunking         │       │ FAISS Semantic   │
       └────────┬─────────┘       │ Search           │
                ▼                 └────────┬─────────┘
       ┌──────────────────┐                │
       │ Embeddings       │◄───────────────┘
       └────────┬─────────┘                │
                ▼                          ▼
       ┌────────────────────────────────────────────┐
       │              RAG Context                   │
       └────────────────────┬───────────────────────┘
                            │
                            ▼
                  ┌──────────────────┐
                  │ Gemini LLM       │
                  │ Answer Generation│
                  └────────┬─────────┘
                           │
                           ▼
                  ┌──────────────────┐
                  │ Answer + Sources │
                  └──────────────────┘
🛠️ Technology Stack
Frontend
React
Vite
JavaScript
CSS
Backend
Python
FastAPI
Uvicorn
Document Processing
PyMuPDF
Tesseract OCR
Text cleaning
Custom chunking pipeline
Retrieval
Sentence embeddings
FAISS
Semantic similarity search
Database
PostgreSQL
SQLAlchemy
Generative AI
Google Gemini
API
REST
OpenAPI / Swagger
✨ Current Features
📄 PDF document upload
🔍 Text extraction
👁️ OCR support for scanned documents
✂️ Document chunking
🧠 Text embeddings
⚡ FAISS vector search
🎯 Document-specific retrieval
🤖 Gemini-powered answer generation
📚 Source information with responses
🌐 React-based interface
🚀 FastAPI backend
🗄️ PostgreSQL document/chunk metadata storage
🔌 REST API
📖 Swagger/OpenAPI documentation
🔄 Example

Suppose a user uploads:

result 6th sem.pdf

The document contains:

CGPA : 8.31

The user asks:

What is the CGPA mentioned in the result?

DocPilot processes the question:

Question
   ↓
Embedding
   ↓
Semantic Search
   ↓
Relevant Chunk
   ↓
"CGPA : 8.31"
   ↓
Gemini
   ↓
"The CGPA mentioned is 8.31."

And returns the answer together with source information.

📁 Project Structure
DocPilot/
│
├── apps/
│   │
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   ├── db/
│   │   │   └── services/
│   │   │
│   │   ├── database.py
│   │   ├── main.py
│   │   └── test_*.py
│   │
│   └── frontend/
│       ├── src/
│       │   ├── services/
│       │   ├── App.jsx
│       │   ├── App.css
│       │   └── main.jsx
│       ├── package.json
│       └── vite.config.js
│
├── data/
│   ├── uploads/
│   └── faiss/
│
└── .gitignore
🚀 Running Locally
1. Clone
git clone https://github.com/omchaudhary360/DocPilot.git
cd DocPilot
2. Backend
cd apps/backend

Create and activate a virtual environment:

python -m venv .venv

Windows:

.venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Configure the required environment variables, including the Gemini API configuration and PostgreSQL connection.

Then start the backend:

python -m uvicorn main:app --reload

Backend:

http://127.0.0.1:8000

Swagger:

http://127.0.0.1:8000/docs
3. Frontend

Open another terminal:

cd apps/frontend

Install dependencies:

npm install

Start:

npm run dev

Frontend:

http://localhost:5173
📡 API Endpoints
Health
GET /api/v1/health
Upload Document
POST /api/v1/documents/upload

Accepts:

multipart/form-data

with a PDF file.

Chat
POST /api/v1/chat

Example:

{
  "question": "What is the CGPA mentioned in the result?",
  "document_id": 3,
  "top_k": 3
}

Response:

{
  "answer": "Based on the provided document, the CGPA mentioned is 8.31.",
  "sources": [
    {
      "document": "result 6th sem.pdf",
      "page": 1,
      "chunk_id": 35,
      "score": 0.51
    }
  ]
}
🔮 Roadmap

DocPilot is currently a working RAG prototype and the architecture is designed to grow into a more complete document intelligence platform.

Planned improvements include:

 Multi-document conversations
 Document comparison
 Automatic document summarization
 Structured information extraction
 Better conversation memory
 Improved OCR pipeline
 Authentication and user accounts
 Document-level access control
 Production vector database
 Cloud deployment
 Streaming AI responses
 Evaluation and retrieval-quality metrics
 Advanced document formats beyond PDF
🎯 Project Vision

The long-term goal of DocPilot is not simply to build another "chat with PDF" application.

The goal is to build a system where documents become interactive sources of knowledge.

Instead of:

Search → Open document → Find information → Read → Understand

the experience becomes:

Ask → Retrieve → Understand → Answer → Verify

That shift can make large collections of documents significantly easier to work with.

👨‍💻 Built By

Om Chaudhary

B.Tech — Artificial Intelligence & Machine Learning

GitHub: @omchaudhary360