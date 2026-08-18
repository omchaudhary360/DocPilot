import json
from pathlib import Path

import faiss
import numpy as np


FAISS_DIR = Path("../../data/faiss")
INDEX_PATH = FAISS_DIR / "documents.index"
MAPPING_PATH = FAISS_DIR / "chunk_mapping.json"


def load_index_and_mapping():
    """
    Load the existing FAISS index and chunk mapping.
    """

    if not INDEX_PATH.exists() or not MAPPING_PATH.exists():
        return None, {}

    index = faiss.read_index(str(INDEX_PATH))

    with MAPPING_PATH.open("r", encoding="utf-8") as file:
        mapping = json.load(file)

    return index, mapping


def add_embeddings_to_index(
    embeddings: list[list[float]],
    chunk_ids: list[int]
):
    """
    Add new embeddings to the existing FAISS index.

    If no index exists, create a new one.
    """

    if not embeddings:
        raise ValueError("No embeddings provided.")

    vectors = np.array(
        embeddings,
        dtype="float32"
    )

    dimension = vectors.shape[1]

    index, mapping = load_index_and_mapping()

    if index is None:
        index = faiss.IndexFlatIP(dimension)

    if index.d != dimension:
        raise ValueError(
            "Embedding dimension does not match the FAISS index."
        )

    start_position = index.ntotal

    index.add(vectors)

    for offset, chunk_id in enumerate(chunk_ids):
        position = start_position + offset
        mapping[str(position)] = chunk_id

    FAISS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    faiss.write_index(
        index,
        str(INDEX_PATH)
    )

    with MAPPING_PATH.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            mapping,
            file,
            indent=2
        )

    return index