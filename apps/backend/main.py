from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.documents.routes import router as documents_router
from app.api.v1.chat.routes import router as chat_router
from app.api.v1.conversations.routes import router as conversations_router


app = FastAPI(
    title="AI Document Intelligence API",
    description="AI-powered document analysis and RAG system",
    version="1.0.0"
)


# =========================================
# CORS
# =========================================

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


app.add_middleware(
    CORSMiddleware,

    allow_origins=ALLOWED_ORIGINS,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================
# ROUTERS
# =========================================

app.include_router(
    documents_router,
    prefix="/api/v1"
)

app.include_router(
    chat_router,
    prefix="/api/v1"
)

app.include_router(
    conversations_router,
    prefix="/api/v1"
)


# =========================================
# HEALTH
# =========================================

@app.get("/api/v1/health")
def health_check():

    return {
        "status": "healthy",
        "message": "AI Document Intelligence API is running"
    }