import json
from pathlib import Path

import faiss
import numpy as np
from sqlalchemy.orm import Session

from app.db.models.chunk import DocumentChunk
from app.db.models.document import Document
from app.services.embedding_service import generate_embedding


FAISS_DIR = Path("../../data/faiss")
INDEX_PATH = FAISS_DIR / "documents.index"
MAPPING_PATH = FAISS_DIR / "chunk_mapping.json"


def search_similar_chunks(
    db: Session,
    query: str,
    document_id: int | None = None,
    top_k: int = 3
) -> list[dict]:
    """
    Search FAISS and optionally restrict results
    to a specific document.
    """

    if not INDEX_PATH.exists():
        raise FileNotFoundError("FAISS index not found.")

    if not MAPPING_PATH.exists():
        raise FileNotFoundError("FAISS chunk mapping not found.")

    index = faiss.read_index(str(INDEX_PATH))

    with MAPPING_PATH.open(
        "r",
        encoding="utf-8"
    ) as file:
        mapping = json.load(file)

    query_embedding = generate_embedding(query)

    query_vector = np.array(
        [query_embedding],
        dtype="float32"
    )

    # Search more candidates because we may filter
    # some of them by document_id.
    search_k = min(
        max(top_k * 10, 20),
        index.ntotal
    )

    scores, positions = index.search(
        query_vector,
        search_k
    )

    results = []

    for score, position in zip(
        scores[0],
        positions[0]
    ):

        if position == -1:
            continue

        chunk_id = mapping.get(str(position))

        if chunk_id is None:
            continue

        chunk = (
            db.query(DocumentChunk)
            .filter(DocumentChunk.id == chunk_id)
            .first()
        )

        if chunk is None:
            continue

        # Document-specific filtering
        if (
            document_id is not None
            and chunk.document_id != document_id
        ):
            continue

        document = (
            db.query(Document)
            .filter(Document.id == chunk.document_id)
            .first()
        )

        if document is None:
            continue

        results.append(
            {
                "chunk_id": chunk.id,
                "document_id": document.id,
                "document_name": document.original_name,
                "page_number": chunk.page_number,
                "score": float(score),
                "text": chunk.text_content,
            }
        )

        # Stop once we have enough relevant chunks
        if len(results) >= top_k:
            break

    return results