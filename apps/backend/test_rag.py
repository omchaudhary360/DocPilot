from database import SessionLocal
from app.services.rag_service import answer_question


db = SessionLocal()

try:
    question = "What is the objective of this project?"

    result = answer_question(
        db=db,
        question=question,
        top_k=3
    )

    print("\n================ ANSWER ================")
    print(result["answer"])

    print("\n================ SOURCES ================")

    for source in result["sources"]:
        print(
            f"Document: {source['document']}"
        )
        print(
            f"Page: {source['page']}"
        )
        print(
            f"Chunk ID: {source['chunk_id']}"
        )
        print(
            f"Score: {source['score']:.4f}"
        )
        print("----------------------------------------")

finally:
    db.close()