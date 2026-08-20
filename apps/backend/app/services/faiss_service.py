import json
from pathlib import Path
import faiss
import numpy as np
from datetime import datetime
import os


# Get FAISS directory from environment or use default
FAISS_DIR = Path(os.getenv("FAISS_DIR", "data/faiss"))
INDEX_PATH = FAISS_DIR / "documents.index"
MAPPING_PATH = FAISS_DIR / "chunk_mapping.json"
METADATA_PATH = FAISS_DIR / "chunk_metadata.json"
VERSION_FILE = FAISS_DIR / "version.txt"


def ensure_faiss_dir():
    """Create FAISS directory if it doesn't exist"""
    FAISS_DIR.mkdir(parents=True, exist_ok=True)


def load_index_and_mapping():
    """
    Load existing FAISS index and mappings.
    
    Returns: (index, mapping, metadata) or (None, {}, {})
    """
    
    ensure_faiss_dir()
    
    if not INDEX_PATH.exists() or not MAPPING_PATH.exists():
        return None, {}, {}
    
    try:
        index = faiss.read_index(str(INDEX_PATH))
        
        with MAPPING_PATH.open("r", encoding="utf-8") as f:
            mapping = json.load(f)
        
        metadata = {}
        if METADATA_PATH.exists():
            with METADATA_PATH.open("r", encoding="utf-8") as f:
                metadata = json.load(f)
        
        return index, mapping, metadata
        
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        return None, {}, {}


def add_embeddings_to_index(
    embeddings: list[list[float]],
    chunk_ids: list[int],
    document_id: int,
    document_metadata: dict | None = None
) -> tuple[object, dict, dict]:
    """
    Add new embeddings to FAISS index.
    
    Parameters:
    - embeddings: List of embedding vectors
    - chunk_ids: List of chunk IDs corresponding to embeddings
    - document_id: Document these chunks belong to
    - document_metadata: Optional metadata about chunks
    
    Returns: (index, mapping, metadata)
    """
    
    if not embeddings:
        raise ValueError("No embeddings provided")
    
    ensure_faiss_dir()
    
    vectors = np.array(embeddings, dtype="float32")
    dimension = vectors.shape[1]
    
    # Load existing
    index, mapping, metadata = load_index_and_mapping()
    
    # Create new index if needed
    if index is None:
        index = faiss.IndexFlatIP(dimension)
    
    # Verify dimension matches
    if index.d != dimension:
        raise ValueError(
            f"Embedding dimension mismatch. "
            f"Index expects {index.d}, got {dimension}"
        )
    
    # Get start position for new vectors
    start_position = index.ntotal
    
    # Add vectors to index
    index.add(vectors)
    
    # Update mappings
    for offset, chunk_id in enumerate(chunk_ids):
        position = start_position + offset
        mapping[str(position)] = int(chunk_id)
        
        # Store metadata
        if document_metadata and offset < len(document_metadata):
            meta = document_metadata[offset]
            metadata[str(chunk_id)] = {
                "document_id": document_id,
                "position": position,
                "page_number": meta.get("page_number"),
                "chunk_index": meta.get("chunk_index"),
                "added_at": datetime.utcnow().isoformat(),
            }
        else:
            metadata[str(chunk_id)] = {
                "document_id": document_id,
                "position": position,
                "added_at": datetime.utcnow().isoformat(),
            }
    
    # Save index
    faiss.write_index(index, str(INDEX_PATH))
    
    # Save mappings
    with MAPPING_PATH.open("w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2)
    
    # Save metadata
    with METADATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    
    # Update version
    with VERSION_FILE.open("w") as f:
        f.write(datetime.utcnow().isoformat())
    
    return index, mapping, metadata


def remove_document_from_index(document_id: int) -> bool:
    """
    Remove all chunks belonging to a document from FAISS index.
    
    This requires rebuilding the index (FAISS doesn't support deletion).
    """
    
    ensure_faiss_dir()
    
    index, mapping, metadata = load_index_and_mapping()
    
    if index is None:
        return False
    
    # Find positions to remove
    positions_to_remove = []
    mapping_to_keep = {}
    metadata_to_keep = {}
    
    for position_str, chunk_id in mapping.items():
        chunk_id_int = int(chunk_id) if isinstance(chunk_id, str) else chunk_id
        chunk_metadata = metadata.get(str(chunk_id_int), {})
        
        if chunk_metadata.get("document_id") == document_id:
            positions_to_remove.append(int(position_str))
        else:
            mapping_to_keep[position_str] = chunk_id
            if str(chunk_id_int) in metadata:
                metadata_to_keep[str(chunk_id_int)] = metadata[str(chunk_id_int)]
    
    if not positions_to_remove:
        return False
    
    # Rebuild index without removed vectors
    # This is necessary because FAISS IndexFlatIP doesn't support deletion
    # Extract all vectors except those to remove
    kept_vectors = []
    new_position = 0
    new_mapping = {}
    
    for old_position in range(index.ntotal):
        if old_position not in positions_to_remove:
            # Get vector at this position
            vector = index.reconstruct(old_position).reshape(1, -1)
            kept_vectors.append(vector)
            
            # Find original chunk_id
            old_chunk_id = mapping.get(str(old_position))
            if old_chunk_id is not None:
                new_mapping[str(new_position)] = old_chunk_id
                new_position += 1
    
    # Create new index
    if kept_vectors:
        all_vectors = np.vstack(kept_vectors)
        new_index = faiss.IndexFlatIP(index.d)
        new_index.add(all_vectors)
    else:
        new_index = faiss.IndexFlatIP(index.d)
    
    # Save
    faiss.write_index(new_index, str(INDEX_PATH))
    
    with MAPPING_PATH.open("w", encoding="utf-8") as f:
        json.dump(new_mapping, f, indent=2)
    
    with METADATA_PATH.open("w", encoding="utf-8") as f:
        json.dump(metadata_to_keep, f, indent=2)
    
    return True


def get_index_status() -> dict:
    """Get FAISS index statistics"""
    
    ensure_faiss_dir()
    index, mapping, metadata = load_index_and_mapping()
    
    if index is None:
        return {
            "exists": False,
            "total_vectors": 0,
            "dimension": 0,
            "total_documents": 0,
        }
    
    # Count unique documents
    document_ids = set()
    for meta in metadata.values():
        if isinstance(meta, dict) and "document_id" in meta:
            document_ids.add(meta["document_id"])
    
    return {
        "exists": True,
        "total_vectors": index.ntotal,
        "dimension": index.d,
        "total_chunks": len(mapping),
        "total_documents": len(document_ids),
    }