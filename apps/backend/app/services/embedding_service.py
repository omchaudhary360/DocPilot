from sentence_transformers import SentenceTransformer
import os


# Model configuration
MODEL_NAME = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# Initialize model
try:
    model = SentenceTransformer(MODEL_NAME)
except Exception as e:
    print(f"Warning: Failed to load embedding model {MODEL_NAME}: {e}")
    print("Falling back to default model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text: str) -> list[float]:
    """
    Generate embedding for a single text.
    
    Returns: Normalized embedding vector
    """
    
    if not text or not text.strip():
        # Return zero vector if text is empty
        return [0.0] * model.get_sentence_embedding_dimension()
    
    try:
        embedding = model.encode(
            text.strip(),
            normalize_embeddings=True
        )
        return embedding.tolist()
    except Exception as e:
        print(f"Embedding generation error: {e}")
        return [0.0] * model.get_sentence_embedding_dimension()


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for multiple texts.
    
    Returns: List of normalized embedding vectors
    """
    
    if not texts:
        return []
    
    try:
        embeddings = model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embeddings.tolist()
    except Exception as e:
        print(f"Batch embedding error: {e}")
        # Return zero vectors
        dim = model.get_sentence_embedding_dimension()
        return [[0.0] * dim for _ in texts]


def get_embedding_dimension() -> int:
    """Get the dimension of embeddings produced by the model"""
    return model.get_sentence_embedding_dimension()