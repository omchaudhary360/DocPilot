import json
import re
from pathlib import Path
import faiss
import numpy as np
from sqlalchemy.orm import Session

from app.db.models.chunk import DocumentChunk
from app.db.models.document import Document
from app.services.embedding_service import generate_embedding
from app.services.faiss_service import load_index_and_mapping


# Retrieval tuning
CANDIDATE_POOL_SIZE = 50
RERANK_TOP_K = 10
MAX_FINAL_RESULTS = 8

MIN_SEMANTIC_SCORE = 0.15
MIN_COMBINED_SCORE = 0.18


# Stop words for query processing
STOP_WORDS = {
    "the", "a", "an",
    "is", "are", "was", "were", "be", "been",
    "what", "which", "who", "whom", "whose",
    "where", "when", "why", "how",
    "much", "many", "some", "any",
    "does", "did", "do", "have", "has", "had",
    "can", "could", "would", "should", "will", "shall",
    "please", "tell", "me", "us",
    "about", "this", "that", "these", "those",
    "document", "pdf", "file", "page",
    "mentioned", "mention", "show", "show me",
    "find", "provide", "give", "explain",
    "state", "according", "accordingto", "based",
    "in", "on", "at", "to", "from", "by",
    "if", "then", "else", "or", "and", "not",
}


def normalize_text(text: str) -> str:
    """Normalize text for matching"""
    if not text:
        return ""
    
    text = text.lower()
    
    # Preserve currency amounts
    text = text.replace("₹", " rs ")
    text = text.replace("$", " dollar ")
    text = text.replace("€", " euro ")
    text = text.replace("£", " pound ")
    
    # Normalize separators
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    text = text.replace("_", " ")
    
    # Remove punctuation but keep alphanumeric
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    
    return text.strip()


def get_query_tokens(query: str) -> set[str]:
    """Extract meaningful tokens from query"""
    normalized = normalize_text(query)
    tokens = normalized.split()
    
    # Keep tokens >= 2 chars and not stop words
    return {
        token for token in tokens
        if len(token) >= 2 and token not in STOP_WORDS
    }


def extract_values(text: str) -> set[str]:
    """
    Extract factual values from text.
    
    Captures:
    - Numbers and decimals
    - Dates
    - Percentages
    - IDs and codes
    """
    if not text:
        return set()
    
    values = set()
    
    # Decimal/integer values (including rollnos, IDs)
    values.update(re.findall(r"\b\d+(?:\.\d+)?\b", text))
    
    # Dates: DD.MM.YYYY, DD/MM/YYYY, DD-MM-YYYY
    values.update(re.findall(
        r"\b\d{1,4}[./-]\d{1,2}[./-]\d{1,4}\b",
        text
    ))
    
    # Percentages
    values.update(re.findall(r"\b\d+(?:\.\d+)?%", text))
    
    # Email-like patterns
    values.update(re.findall(r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\b", text))
    
    # Phone-like patterns
    values.update(re.findall(r"\b\d{10}\b|\b\+\d{1,3}\s?\d+\b", text))
    
    return {
        normalize_text(v) for v in values if v
    }


def calculate_lexical_score(query: str, text: str) -> float:
    """Score based on keyword overlap"""
    query_tokens = get_query_tokens(query)
    
    if not query_tokens:
        return 0.0
    
    text_tokens = set(normalize_text(text).split())
    
    if not text_tokens:
        return 0.0
    
    overlap = query_tokens & text_tokens
    return len(overlap) / len(query_tokens)


def calculate_value_score(query: str, text: str) -> float:
    """Score based on exact factual value matching"""
    query_values = extract_values(query)
    
    if not query_values:
        return 0.0
    
    text_values = extract_values(text)
    
    if not text_values:
        return 0.0
    
    matched = query_values & text_values
    return len(matched) / len(query_values)


def calculate_phrase_score(query: str, text: str) -> float:
    """Score based on phrase presence"""
    query_normalized = normalize_text(query)
    text_normalized = normalize_text(text)
    
    if not query_normalized:
        return 0.0
    
    # Exact phrase match
    if query_normalized in text_normalized:
        return 1.0
    
    # Partial multi-word matches
    query_tokens = get_query_tokens(query)
    if not query_tokens:
        return 0.0
    
    matches = sum(1 for token in query_tokens if token in text_normalized)
    return min(matches / len(query_tokens), 1.0)


def search_similar_chunks(
    db: Session,
    query: str,
    document_id: int | None = None,
    top_k: int = 5
) -> list[dict]:
    """
    Hybrid retrieval: semantic + lexical + value matching.
    
    1. Search FAISS for semantic candidates
    2. Rerank using hybrid scoring
    3. Filter by confidence
    4. Return top results
    """
    
    if not query or not query.strip():
        return []
    
    query = query.strip()
    top_k = min(max(top_k, 1), MAX_FINAL_RESULTS)
    
    # Load FAISS
    from app.services.faiss_service import INDEX_PATH, MAPPING_PATH
    
    if not INDEX_PATH.exists() or not MAPPING_PATH.exists():
        return []
    
    try:
        index = faiss.read_index(str(INDEX_PATH))
        
        if index.ntotal == 0:
            return []
        
        with MAPPING_PATH.open("r", encoding="utf-8") as f:
            mapping = json.load(f)
            
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        return []
    
    # Generate query embedding
    try:
        query_embedding = generate_embedding(query)
    except Exception as e:
        print(f"Embedding generation failed: {e}")
        return []
    
    query_vector = np.asarray([query_embedding], dtype="float32")
    
    # Search FAISS for candidates
    search_k = min(
        CANDIDATE_POOL_SIZE,
        index.ntotal
    )
    
    try:
        scores, positions = index.search(query_vector, search_k)
    except Exception as e:
        print(f"FAISS search failed: {e}")
        return []
    
    # Build candidate list
    candidates = []
    seen_chunk_ids = set()
    
    for semantic_score, position in zip(scores[0], positions[0]):
        if position == -1:
            continue
        
        chunk_id_str = mapping.get(str(int(position)))
        if chunk_id_str is None:
            continue
        
        try:
            chunk_id = int(chunk_id_str)
        except (ValueError, TypeError):
            continue
        
        if chunk_id in seen_chunk_ids:
            continue
        
        seen_chunk_ids.add(chunk_id)
        
        candidates.append({
            "chunk_id": chunk_id,
            "semantic_score": float(semantic_score)
        })
    
    if not candidates:
        return []
    
    # Fetch chunks from database
    chunk_ids = [c["chunk_id"] for c in candidates]
    
    rows = db.query(DocumentChunk, Document).join(
        Document,
        Document.id == DocumentChunk.document_id
    ).filter(DocumentChunk.id.in_(chunk_ids)).all()
    
    chunk_lookup = {
        chunk.id: (chunk, document)
        for chunk, document in rows
    }
    
    # Rerank with hybrid scoring
    results = []
    
    for candidate in candidates:
        chunk_id = candidate["chunk_id"]
        data = chunk_lookup.get(chunk_id)
        
        if data is None:
            continue
        
        chunk, document = data
        
        # Document filter
        if document_id is not None and chunk.document_id != document_id:
            continue
        
        # Empty chunk check
        if not chunk.text_content or not chunk.text_content.strip():
            continue
        
        text = chunk.text_content
        semantic_score = candidate["semantic_score"]
        
        # Calculate hybrid scores
        lexical_score = calculate_lexical_score(query, text)
        value_score = calculate_value_score(query, text)
        phrase_score = calculate_phrase_score(query, text)
        
        # Combined score
        combined_score = (
            0.60 * semantic_score +
            0.20 * lexical_score +
            0.15 * value_score +
            0.05 * phrase_score
        )
        
        results.append({
            "chunk_id": chunk.id,
            "document_id": document.id,
            "document_name": document.original_name,
            "page_number": chunk.page_number,
            "score": combined_score,
            "semantic_score": semantic_score,
            "lexical_score": lexical_score,
            "value_score": value_score,
            "phrase_score": phrase_score,
            "text": text,
        })
    
    # Sort by combined score
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # Quality filtering
    filtered_results = []
    
    for result in results:
        # Strong exact value match
        if result["value_score"] > 0:
            filtered_results.append(result)
            continue
        
        # Strong lexical evidence
        if result["lexical_score"] >= 0.30:
            filtered_results.append(result)
            continue
        
        # Semantic + combined threshold
        if (result["semantic_score"] >= MIN_SEMANTIC_SCORE and
            result["score"] >= MIN_COMBINED_SCORE):
            filtered_results.append(result)
    
    # Fallback: if no high-quality results, return top semantic matches
    if not filtered_results and results:
        filtered_results = results[:top_k]
    
    return filtered_results[:top_k]