from sqlalchemy.orm import Session

from app.db.models.chunk import DocumentChunk
from app.db.models.document import Document

from app.services.retrieval_service import search_similar_chunks
from app.services.llm_service import generate_answer


# =========================================================
# SUMMARY QUERY DETECTION
# =========================================================

SUMMARY_KEYWORDS = {
    "summarize",
    "summarise",
    "summary",
    "overview",
    "key points",
    "main points",
    "important points",
    "highlights",
    "give me a summary",
    "what is this document about",
    "explain this document",
}


def is_summary_query(question: str) -> bool:

    question_lower = question.strip().lower()

    return any(
        keyword in question_lower
        for keyword in SUMMARY_KEYWORDS
    )


# =========================================================
# BUILD CONTEXT
# =========================================================

def build_context(
    results: list[dict]
) -> str:

    context_parts = []

    for index, result in enumerate(
        results,
        start=1
    ):

        context_parts.append(
            f"""
SOURCE {index}

Document:
{result["document_name"]}

Page:
{result["page_number"]}

Content:
{result["text"]}
"""
        )

    return "\n".join(
        context_parts
    )


# =========================================================
# GET DOCUMENT CHUNKS
# =========================================================

def get_document_chunks(
    db: Session,
    document_id: int
) -> list[dict]:

    rows = (
        db.query(
            DocumentChunk,
            Document
        )
        .join(
            Document,
            Document.id ==
            DocumentChunk.document_id
        )
        .filter(
            DocumentChunk.document_id ==
            document_id
        )
        .order_by(
            DocumentChunk.chunk_index
        )
        .all()
    )

    results = []

    for chunk, document in rows:

        if not chunk.text_content:
            continue

        text = chunk.text_content.strip()

        if not text:
            continue

        results.append(
            {
                "chunk_id": chunk.id,

                "document_id":
                    document.id,

                "document_name":
                    document.original_name,

                "page_number":
                    chunk.page_number,

                "score":
                    1.0,

                "text":
                    text,
            }
        )

    return results


# =========================================================
# BUILD SUMMARY CONTEXT
# =========================================================

def build_summary_context(
    results: list[dict]
) -> str:
    """
    Keep document order and include as much of the document
    as reasonably possible.

    No document-specific assumptions.
    """

    if not results:
        return ""

    # Limit by approximate character count instead of
    # blindly taking first N chunks.
    MAX_CONTEXT_CHARS = 90000

    selected = []

    current_length = 0

    for result in results:

        text_length = len(
            result["text"]
        )

        if (
            current_length +
            text_length >
            MAX_CONTEXT_CHARS
        ):
            break

        selected.append(
            result
        )

        current_length += text_length

    # If even the first chunk is unusually large,
    # still provide it.
    if not selected:
        selected.append(
            results[0]
        )

    return build_context(
        selected
    )


# =========================================================
# ANSWER QUESTION
# =========================================================

def answer_question(
    db: Session,
    question: str,
    document_id: int | None = None,
    top_k: int = 3
) -> dict:

    # =====================================================
    # VALIDATE QUESTION
    # =====================================================

    if not question or not question.strip():

        return {
            "answer":
                "Please provide a question.",
            "sources": []
        }

    question = question.strip()


    # =====================================================
    # DOCUMENT REQUIRED
    # =====================================================

    if document_id is None:

        return {
            "answer":
                "Please upload or select a document first.",
            "sources": []
        }


    # =====================================================
    # VERIFY DOCUMENT
    # =====================================================

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id
        )
        .first()
    )

    if document is None:

        return {
            "answer":
                "The selected document could not be found.",
            "sources": []
        }


    # =====================================================
    # SUMMARY
    # =====================================================

    if is_summary_query(question):

        results = get_document_chunks(
            db=db,
            document_id=document_id
        )

        if not results:

            return {
                "answer":
                    "I could not find any readable content in the uploaded document.",
                "sources": []
            }

        context = build_summary_context(
            results
        )

        answer = generate_answer(
            question=question,
            context=context,
            is_summary=True
        )

        # Sources should represent the content actually
        # supplied to the model.
        source_results = results

        return {
            "answer": answer,

            "sources": [
                {
                    "document":
                        result["document_name"],

                    "page":
                        result["page_number"],

                    "chunk_id":
                        result["chunk_id"],

                    "score":
                        result["score"],
                }

                for result in source_results
            ]
        }


    # =====================================================
    # NORMAL QUESTION
    # =====================================================

    results = search_similar_chunks(
        db=db,
        query=question,
        document_id=document_id,
        top_k=top_k
    )


    # =====================================================
    # NO RESULTS
    # =====================================================

    if not results:

        return {
            "answer":
                "I couldn't find this information in the uploaded document.",
            "sources": []
        }


    # =====================================================
    # BUILD CONTEXT
    # =====================================================

    context = build_context(
        results
    )


    # =====================================================
    # GENERATE ANSWER
    # =====================================================

    answer = generate_answer(
        question=question,
        context=context,
        is_summary=False
    )


    # =====================================================
    # SOURCES
    # =====================================================

    sources = [
        {
            "document":
                result["document_name"],

            "page":
                result["page_number"],

            "chunk_id":
                result["chunk_id"],

            "score":
                result["score"],
        }

        for result in results
    ]


    # =====================================================
    # RESPONSE
    # =====================================================

    return {
        "answer": answer,
        "sources": sources
    }