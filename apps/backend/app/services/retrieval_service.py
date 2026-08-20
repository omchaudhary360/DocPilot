import json
import re
from pathlib import Path

import faiss
import numpy as np
from sqlalchemy.orm import Session

from app.db.models.chunk import DocumentChunk
from app.db.models.document import Document
from app.services.embedding_service import generate_embedding


# =========================================================
# PATHS
# =========================================================

FAISS_DIR = Path("../../data/faiss")

INDEX_PATH = FAISS_DIR / "documents.index"
MAPPING_PATH = FAISS_DIR / "chunk_mapping.json"


# =========================================================
# RETRIEVAL SETTINGS
# =========================================================

MIN_SEMANTIC_SCORE = 0.12
MIN_COMBINED_SCORE = 0.16

CANDIDATE_MULTIPLIER = 20
MIN_CANDIDATES = 40

MAX_TOP_K = 8


# =========================================================
# STOP WORDS
# =========================================================

STOP_WORDS = {
    "the", "a", "an",
    "is", "are", "was", "were",
    "what", "which", "who",
    "where", "when", "why", "how",
    "much", "many",
    "does", "did", "do",
    "can", "could", "would",
    "should", "will",
    "please", "tell", "me",
    "about", "this", "that",
    "document", "pdf",
    "mentioned", "mention",
    "give", "show",
    "find", "provide",
    "explain", "state",
    "according", "accordingto",
}


# =========================================================
# TEXT NORMALIZATION
# =========================================================

def normalize_text(text: str) -> str:

    if not text:
        return ""

    text = text.lower()

    # Currency / common symbols
    text = text.replace("₹", " rs ")
    text = text.replace("$", " dollar ")
    text = text.replace("€", " euro ")
    text = text.replace("£", " pound ")

    # Normalize separators
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    text = text.replace("_", " ")

    # Keep letters and numbers
    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# =========================================================
# QUERY TOKENS
# =========================================================

def get_query_tokens(query: str) -> set[str]:

    normalized = normalize_text(query)

    tokens = normalized.split()

    return {
        token
        for token in tokens
        if len(token) >= 2
        and token not in STOP_WORDS
    }


# =========================================================
# EXACT VALUE EXTRACTION
# =========================================================

def extract_values(text: str) -> set[str]:
    """
    Extract potentially important factual values.

    Handles:
    - numbers
    - decimals
    - dates
    - IDs
    - percentages
    - amounts
    """

    if not text:
        return set()

    values = set()

    # Decimal / integer values
    values.update(
        re.findall(
            r"\b\d+(?:\.\d+)?\b",
            text
        )
    )

    # Dates like:
    # 09.07.2026
    # 09/07/2026
    # 09-07-2026
    values.update(
        re.findall(
            r"\b\d{1,4}[./-]\d{1,2}[./-]\d{1,4}\b",
            text
        )
    )

    # Percentages
    values.update(
        re.findall(
            r"\b\d+(?:\.\d+)?%",
            text
        )
    )

    return {
        normalize_text(value)
        for value in values
        if value
    }


# =========================================================
# LEXICAL SCORE
# =========================================================

def calculate_lexical_score(
    query: str,
    text: str
) -> float:

    query_tokens = get_query_tokens(query)

    if not query_tokens:
        return 0.0

    text_tokens = set(
        normalize_text(text).split()
    )

    if not text_tokens:
        return 0.0

    overlap = (
        query_tokens &
        text_tokens
    )

    return (
        len(overlap) /
        len(query_tokens)
    )


# =========================================================
# VALUE MATCH SCORE
# =========================================================

def calculate_value_score(
    query: str,
    text: str
) -> float:
    """
    Gives additional importance to exact factual values.

    This is completely document-agnostic.
    """

    query_values = extract_values(query)

    if not query_values:
        return 0.0

    text_values = extract_values(text)

    if not text_values:
        return 0.0

    matched = (
        query_values &
        text_values
    )

    return (
        len(matched) /
        len(query_values)
    )


# =========================================================
# TEXT TOKEN SIMILARITY
# =========================================================

def calculate_phrase_score(
    query: str,
    text: str
) -> float:

    query_normalized = normalize_text(query)
    text_normalized = normalize_text(text)

    if not query_normalized:
        return 0.0

    if query_normalized in text_normalized:
        return 1.0

    query_tokens = get_query_tokens(query)

    if not query_tokens:
        return 0.0

    # Check important 2-word combinations
    query_words = list(query_tokens)

    matches = 0

    for word in query_words:

        if word in text_normalized:
            matches += 1

    return min(
        matches / len(query_tokens),
        1.0
    )


# =========================================================
# SEARCH SIMILAR CHUNKS
# =========================================================

def search_similar_chunks(
    db: Session,
    query: str,
    document_id: int | None = None,
    top_k: int = 3
) -> list[dict]:

    # =====================================================
    # VALIDATE
    # =====================================================

    if not query or not query.strip():
        return []

    query = query.strip()

    if top_k <= 0:
        return []

    top_k = min(
        top_k,
        MAX_TOP_K
    )


    # =====================================================
    # CHECK INDEX
    # =====================================================

    if not INDEX_PATH.exists():

        raise FileNotFoundError(
            f"FAISS index not found: {INDEX_PATH}"
        )

    if not MAPPING_PATH.exists():

        raise FileNotFoundError(
            f"FAISS mapping not found: {MAPPING_PATH}"
        )


    # =====================================================
    # LOAD FAISS
    # =====================================================

    index = faiss.read_index(
        str(INDEX_PATH)
    )

    if index.ntotal == 0:
        return []


    # =====================================================
    # LOAD MAPPING
    # =====================================================

    with MAPPING_PATH.open(
        "r",
        encoding="utf-8"
    ) as file:

        mapping = json.load(file)


    # =====================================================
    # EMBEDDING
    # =====================================================

    query_embedding = generate_embedding(
        query
    )

    query_vector = np.asarray(
        [query_embedding],
        dtype="float32"
    )


    # =====================================================
    # CANDIDATE COUNT
    # =====================================================

    search_k = min(
        max(
            top_k * CANDIDATE_MULTIPLIER,
            MIN_CANDIDATES
        ),
        index.ntotal
    )


    # =====================================================
    # FAISS SEARCH
    # =====================================================

    scores, positions = index.search(
        query_vector,
        search_k
    )


    # =====================================================
    # CANDIDATES
    # =====================================================

    candidates = []

    seen_chunks = set()

    for semantic_score, position in zip(
        scores[0],
        positions[0]
    ):

        if position == -1:
            continue

        chunk_id = mapping.get(
            str(position)
        )

        if chunk_id is None:
            continue

        try:
            chunk_id = int(chunk_id)
        except (
            TypeError,
            ValueError
        ):
            continue

        if chunk_id in seen_chunks:
            continue

        seen_chunks.add(
            chunk_id
        )

        candidates.append(
            {
                "chunk_id": chunk_id,
                "semantic_score":
                    float(semantic_score)
            }
        )


    if not candidates:
        return []


    # =====================================================
    # DATABASE FETCH
    # =====================================================

    chunk_ids = [
        candidate["chunk_id"]
        for candidate in candidates
    ]

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
            DocumentChunk.id.in_(chunk_ids)
        )
        .all()
    )


    # =====================================================
    # LOOKUP
    # =====================================================

    chunk_lookup = {
        chunk.id: (
            chunk,
            document
        )
        for chunk, document in rows
    }


    # =====================================================
    # RANK
    # =====================================================

    results = []

    for candidate in candidates:

        chunk_id = candidate["chunk_id"]

        data = chunk_lookup.get(
            chunk_id
        )

        if data is None:
            continue

        chunk, document = data


        # =================================================
        # DOCUMENT FILTER
        # =================================================

        if (
            document_id is not None
            and chunk.document_id != document_id
        ):
            continue


        # =================================================
        # EMPTY CHUNK
        # =================================================

        if (
            not chunk.text_content
            or not chunk.text_content.strip()
        ):
            continue


        text = chunk.text_content

        semantic_score = candidate[
            "semantic_score"
        ]


        # =================================================
        # LEXICAL
        # =================================================

        lexical_score = calculate_lexical_score(
            query,
            text
        )


        # =================================================
        # EXACT VALUES
        # =================================================

        value_score = calculate_value_score(
            query,
            text
        )


        # =================================================
        # PHRASE
        # =================================================

        phrase_score = calculate_phrase_score(
            query,
            text
        )


        # =================================================
        # FINAL SCORE
        # =================================================
        #
        # Semantic remains the primary signal.
        #
        # Lexical helps:
        # names / terms
        #
        # Value helps:
        # numbers / dates / percentages / IDs
        #
        # Phrase helps:
        # natural-language matching
        #

        combined_score = (
            0.60 * semantic_score
            +
            0.20 * lexical_score
            +
            0.15 * value_score
            +
            0.05 * phrase_score
        )


        results.append(
            {
                "chunk_id":
                    chunk.id,

                "document_id":
                    document.id,

                "document_name":
                    document.original_name,

                "page_number":
                    chunk.page_number,

                "score":
                    combined_score,

                "semantic_score":
                    semantic_score,

                "lexical_score":
                    lexical_score,

                "value_score":
                    value_score,

                "phrase_score":
                    phrase_score,

                "text":
                    text,
            }
        )


    # =====================================================
    # SORT
    # =====================================================

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )


    # =====================================================
    # FILTER
    # =====================================================

    filtered_results = []

    for result in results:

        semantic_score = result[
            "semantic_score"
        ]

        lexical_score = result[
            "lexical_score"
        ]

        value_score = result[
            "value_score"
        ]

        combined_score = result[
            "score"
        ]


        # Strong exact value match
        if value_score > 0:
            filtered_results.append(
                result
            )
            continue


        # Strong lexical evidence
        if lexical_score >= 0.25:
            filtered_results.append(
                result
            )
            continue


        # Semantic evidence
        if (
            semantic_score >=
            MIN_SEMANTIC_SCORE
            and
            combined_score >=
            MIN_COMBINED_SCORE
        ):
            filtered_results.append(
                result
            )


    # =====================================================
    # FALLBACK
    # =====================================================

    if not filtered_results:

        filtered_results = results[:top_k]


    # =====================================================
    # RETURN
    # =====================================================

    return filtered_results[:top_k]