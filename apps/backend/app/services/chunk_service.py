import re
from sqlalchemy.orm import Session
from app.db.models.chunk import DocumentChunk


def split_into_semantic_chunks(text: str, max_chunk_size: int = 1000) -> list[str]:
    """
    Split text into semantic chunks using paragraph and sentence boundaries.
    
    Respects:
    - Paragraph breaks (double newlines)
    - Single line breaks
    - Sentence boundaries where possible
    """
    
    if not text or not text.strip():
        return []
    
    # Split by paragraphs first (double newlines)
    paragraphs = re.split(r"\n\s*\n", text)
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # If paragraph itself is larger than max_chunk_size, split by sentences
        if len(paragraph) > max_chunk_size:
            sentences = re.split(r"(?<=[.!?])\s+", paragraph)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                
                if len(current_chunk) + len(sentence) + 2 <= max_chunk_size:
                    if current_chunk:
                        current_chunk += " " + sentence
                    else:
                        current_chunk = sentence
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
        
        else:
            # If adding paragraph keeps us within limit
            if len(current_chunk) + len(paragraph) + 2 <= max_chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph
    
    # Add final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def create_chunks(
    pages: list[dict],
    chunk_size: int = 1000,
    chunk_overlap: int = 0
) -> list[dict]:
    """
    Create chunks from extracted pages with metadata.
    
    Parameters:
    - pages: List of {"page_number": int, "text": str}
    - chunk_size: Target characters per chunk
    - chunk_overlap: Currently not used (set for future implementation)
    
    Returns:
    - List of {"page_number": int, "text": str, "chunk_index": int}
    """
    
    chunks = []
    chunk_index = 0
    
    for page in pages:
        page_number = page["page_number"]
        text = page["text"]
        
        if not text or not text.strip():
            continue
        
        # Split into semantic chunks
        page_chunks = split_into_semantic_chunks(text, max_chunk_size=chunk_size)
        
        for chunk_text in page_chunks:
            if not chunk_text.strip():
                continue
            
            chunks.append({
                "chunk_index": chunk_index,
                "page_number": page_number,
                "text": chunk_text.strip(),
            })
            chunk_index += 1
    
    return chunks


def save_chunks(
    db: Session,
    document_id: int,
    chunks: list[dict]
) -> int:
    """
    Save chunks to database with metadata.
    
    Returns: Number of chunks saved
    """
    
    if not chunks:
        return 0
    
    chunk_objects = []
    
    for chunk_data in chunks:
        chunk_object = DocumentChunk(
            document_id=document_id,
            chunk_index=chunk_data["chunk_index"],
            text_content=chunk_data["text"],
            page_number=chunk_data["page_number"],
            is_indexed=False,
            char_count=len(chunk_data["text"]),
        )
        chunk_objects.append(chunk_object)
    
    db.add_all(chunk_objects)
    db.commit()
    
    return len(chunk_objects)