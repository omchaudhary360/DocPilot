from sqlalchemy.orm import Session

from app.services.retrieval_service import search_similar_chunks
from app.services.llm_service import generate_answer


def build_context(results: list[dict]) -> str:
    """
    Build the context that will be sent to the LLM.
    """

    context_parts = []

    for result in results:
        context_parts.append(
            f"""
Document: {result["document_name"]}
Page: {result["page_number"]}

Content:
{result["text"]}
"""
        )

    return "\n".join(context_parts)


def answer_question(
    db: Session,
    question: str,
    document_id: int | None = None,
    top_k: int = 3
) -> dict:
    """
    Complete RAG pipeline:
    retrieve relevant chunks → build context → generate answer.
    """

    results = search_similar_chunks(
        db=db,
        query=question,
        document_id=document_id,
        top_k=top_k
    )

    if not results:
        return {
            "answer": "I could not find relevant information in the uploaded document.",
            "sources": []
        }

    context = build_context(results)

    answer = generate_answer(
        question=question,
        context=context
    )

    sources = [
        {
            "document": result["document_name"],
            "page": result["page_number"],
            "chunk_id": result["chunk_id"],
            "score": result["score"]
        }
        for result in results
    ]

    return {
        "answer": answer,
        "sources": sources
    }