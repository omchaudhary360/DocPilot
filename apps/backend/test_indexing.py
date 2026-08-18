from database import SessionLocal
from app.services.indexing_service import build_document_index


db = SessionLocal()

try:
    result = build_document_index(
        db=db,
        document_id=1
    )

    print("Indexing completed!")
    print(result)

finally:
    db.close()