from sqlalchemy.orm import Session

from app.db.models.chunk import DocumentChunk
from app.db.models.document import Document
from app.services.retrieval_service import search_similar_chunks
from app.services.llm_service import generate_answer


# Summary detection keywords
SUMMARY_KEYWORDS = {
    "summarize", "summarise", "summary",
    "overview", "key points", "main points",
    "important points", "highlights",
    "give me a summary", "what is this document about",
    "explain this document", "tell me about",
}


def is_summary_query(question: str) -> bool:
    """Detect if query is asking for a summary"""
    question_lower = question.strip().lower()
    return any(
        keyword in question_lower
        for keyword in SUMMARY_KEYWORDS
    )


def build_context(results: list[dict]) -> str:
    """Build context string from retrieved results"""
    context_parts = []
    
    for index, result in enumerate(results, start=1):
        context_parts.append(
            f"""
SOURCE {index}

Document: {result["document_name"]}
Page: {result["page_number"]}

{result["text"]}
"""
        )
    
    return "\n".join(context_parts)


def get_document_chunks(
    db: Session,
    document_id: int,
    max_chars: int = 90000
) -> list[dict]:
    """
    Get all chunks for a document in order, respecting character limit.
    
    Used for summary queries to include full document context.
    """
    
    rows = db.query(DocumentChunk, Document).join(
        Document,
        Document.id == DocumentChunk.document_id
    ).filter(
        DocumentChunk.document_id == document_id
    ).order_by(DocumentChunk.chunk_index).all()
    
    results = []
    current_length = 0
    
    for chunk, document in rows:
        if not chunk.text_content or not chunk.text_content.strip():
            continue
        
        text = chunk.text_content.strip()
        text_length = len(text)
        
        # Check if adding this chunk exceeds limit
        if current_length + text_length > max_chars:
            # If we haven't added anything yet, add the first chunk anyway
            if not results:
                results.append({
                    "chunk_id": chunk.id,
                    "document_id": document.id,
                    "document_name": document.original_name,
                    "page_number": chunk.page_number,
                    "score": 1.0,
                    "text": text,
                })
            break
        
        results.append({
            "chunk_id": chunk.id,
            "document_id": document.id,
            "document_name": document.original_name,
            "page_number": chunk.page_number,
            "score": 1.0,
            "text": text,
        })
        
        current_length += text_length
    
    return results


def answer_question(
    db: Session,
    question: str,
    document_id: int | None = None,
    top_k: int = 5
) -> dict:
    """
    Main RAG pipeline.
    
    For summary queries: retrieves full document
    For factual queries: hybrid retrieval + reranking
    
    Returns:
    {
        "answer": str,
        "sources": [
            {
                "document": str,
                "page": int,
                "chunk_id": int,
                "score": float
            }
        ]
    }
    """
    
    # Validate inputs
    if not question or not question.strip():
        return {
            "answer": "Please provide a question.",
            "sources": []
        }
    
    question = question.strip()
    
    if document_id is None:
        return {
            "answer": "Please upload or select a document first.",
            "sources": []
        }
    
    # Verify document exists
    document = db.query(Document).filter(
        Document.id == document_id
    ).first()
    
    if document is None:
        return {
            "answer": "The selected document could not be found.",
            "sources": []
        }
    
    # Handle summary queries
    if is_summary_query(question):
        results = get_document_chunks(db, document_id)
        
        if not results:
            return {
                "answer": "I could not find any readable content in the document.",
                "sources": []
            }
        
        context = build_context(results)
        answer = generate_answer(
            question=question,
            context=context,
            is_summary=True
        )
        
        return {
            "answer": answer,
            "sources": [
                {
                    "document": result["document_name"],
                    "page": result["page_number"],
                    "chunk_id": result["chunk_id"],
                    "score": result["score"],
                }
                for result in results
            ]
        }
    
    # Handle factual queries
    results = search_similar_chunks(
        db=db,
        query=question,
        document_id=document_id,
        top_k=top_k
    )
    
    if not results:
        return {
            "answer": "I couldn't find this information in the uploaded document.",
            "sources": []
        }
    
    context = build_context(results)
    answer = generate_answer(
        question=question,
        context=context,
        is_summary=False
    )
    
    return {
        "answer": answer,
        "sources": [
            {
                "document": result["document_name"],
                "page": result["page_number"],
                "chunk_id": result["chunk_id"],
                "score": result["score"],
            }
            for result in results
        ]
    }