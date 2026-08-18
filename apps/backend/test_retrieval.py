from database import SessionLocal
from app.services.retrieval_service import search_similar_chunks


db = SessionLocal()

try:
    query = "What is the objective of this project?"

    results = search_similar_chunks(
        db=db,
        query=query,
        top_k=3
    )

    print(f"\nQuery: {query}")
    print(f"Results found: {len(results)}")

    for index, result in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")
        print(f"Chunk ID: {result['chunk_id']}")
        print(f"Document: {result['document_name']}")
        print(f"Page: {result['page_number']}")
        print(f"Score: {result['score']:.4f}")
        print(f"Text: {result['text'][:500]}")

finally:
    db.close()