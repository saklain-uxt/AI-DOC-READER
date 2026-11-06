
import asyncio
from typing import List, Optional

from sentence_transformers import SentenceTransformer


# -----------------------------------------
# 1. Configuration
# -----------------------------------------

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

EMBEDDING_DIMENSION = 384

# Global model instance
embedding_model: Optional[SentenceTransformer] = None


# -----------------------------------------
# 2. Load embedding model
# -----------------------------------------

def get_embedding_model() -> SentenceTransformer:
    """
    Load the embedding model only once.
    Reuse the same model for subsequent requests.
    """

    global embedding_model

    if embedding_model is None:
        embedding_model = SentenceTransformer(MODEL_NAME)

    return embedding_model


# -----------------------------------------
# 3. Generate embeddings for multiple texts
# -----------------------------------------

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for multiple text chunks.

    Args:
        texts: List of text chunks.

    Returns:
        List of normalized 384-dimensional embedding vectors.
    """

    if not texts:
        return []

    # Validate input
    if not all(isinstance(text, str) and text.strip() for text in texts):
        raise ValueError("All texts must be non-empty strings.")

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False
    )

    return embeddings.tolist()


# -----------------------------------------
# 4. Generate embedding for a single text
# -----------------------------------------

def generate_embedding(text: str) -> List[float]:
    """
    Generate an embedding for a single text.
    """

    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text cannot be empty.")

    embeddings = generate_embeddings([text])

    return embeddings[0]


# -----------------------------------------
# 5. Async embedding generation
# -----------------------------------------

async def generate_embeddings_async(
    texts: List[str]
) -> List[List[float]]:
    """
    Run embedding generation in a separate thread
    to avoid blocking FastAPI's event loop.
    """

    return await asyncio.to_thread(
        generate_embeddings,
        texts
    )


async def generate_embedding_async(text: str) -> List[float]:
    """
    Generate a single embedding asynchronously.
    """

    return await asyncio.to_thread(
        generate_embedding,
        text
    )
